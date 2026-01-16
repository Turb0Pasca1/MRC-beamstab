# protocol/protocol.py

from .defs import *
import struct
import time

class ProtocolDecoder:
    # communication protocol information
    command_parameter_struct_map = COMMAND_PARAMETER_STRUCT_MAP
    return_value_struct_map      = RETURN_VALUE_STRUCT_MAP
    ascii_keys                   = ASCII_KEYS
    command_response_map         = COMMAND_RESPONSE_MAP
    error_code_map               = ERROR_CODE_MAP
    error_description_map        = ERROR_DESCRIPTION_MAP

    def __init__(self, connection):
        self.connection = connection

    def send_command(self, command: str, params=None):
        if params is None:
            params = b''
        if not isinstance(command, str):
            raise TypeError('command must be str')
        if not isinstance(params, (bytes, bytearray)):
            raise TypeError('params must be bytes')
        frame = (
            command.encode('ascii') +
            params +
            b';'
        )
        self.connection.write(frame)

    def receive(self, size: int) -> bytes:
        return self.connection.read(size)
        
    # helper functions
    def get_formatter_str(self, fields, map=None):
        '''
        builder for struct formatter string to pack and unpack bytes
        '''
        if map is None:
            map = self.return_value_struct_map
        # high byte first
        fmt = '>'  
        for field in fields:
            if field not in map:
                raise ValueError(f'Field {field} not in return_value_struct_map')
            fmt += map[field]
        return fmt
    
    def acknowledge(self, response):
        '''
        interpret first two bytes of response (0;) as acknowledged message
        '''
        if (response['fe'] != 0) & (response['semi_fe'] != 59):
            raise ValueError('Command has not been acknowledged')

    # decode response of a sent command    
    def decode_response(self, reply, command):
        '''
        decode_response()
        - decodes command response

        return dict of command return keys and values
        '''
        # check command validity
        if command not in self.command_response_map:
            raise ValueError(f'Unknown command {command}')
    
        fields = self.command_response_map[command]
    
        fmt = self.get_formatter_str(fields)

        # check reply length with expected length
        if struct.calcsize(fmt) != len(reply):
            raise ValueError(f'Length of reply {len(reply)} byte does not match length of expected "{command}" length of {struct.calcsize(fmt)} byte.')
          
        # unpack
        unpacked = struct.unpack(fmt, reply)
        response = dict(zip(fields, unpacked))

        self.acknowledge(response)
    
        # handle special cases of keys
        for key, val in result.items():
            # StatusFlag: convert to bit dictionary
            if key == 'StatusFlag':
                bits = format(val, '08b')
                response['StatusFlag'] = dict(zip(self.command_response_map.get('StatusFlag', []), bits))
                continue
    
            # decode fields received as ascii
            if key in self.ascii_keys:
                if isinstance(val, (bytes, bytearray)):
                    response[key] = val.rstrip(b'\x00').decode('ascii')
                elif isinstance(val, int) and 0 <= val <= 127:
                    response[key] = chr(val)
                continue
    
            # map error code
            if key == 'e':
                code = val
                if isinstance(code, (bytes, bytearray)) and len(code) == 1:
                    code = code[0]
    
                error_name = self.error_code_map.get(code, f'UnknownError_0x{code:02X}')
                error_description = self.error_description_map.get(code, 'No description available.')
    
                response['e'] = {
                    'ErrorCode': f'0x{code:02X}',
                    'ErrorName': error_name,
                    'ErrorDescription': error_description
                }
                continue
    
        return response
    
    def get_position(self):
        command = 'S1S'
        self.send_command(command)
        fields = self.command_response_map[command]
        fmt = self.get_formatter_str(fields)
        length = struct.calcsize(fmt)
        raw_reply = self.receive(length)
        return self.decode_response(raw_reply, command)
    
    def get_position_continues(self, r):
        '''
        m: number of transmitted data measurement blocks
           0: continues measurement
           1 <= m <= 65500
        r: time interval 
           1 <= r <= 500 samples/s
        '''
        command = 'SLSmr'
        fields = ['m', 'r']
        fmt = self.get_formatter_str(fields, map=self.command_parameter_struct_map)
        params = struct.pack(fmt, 0, r)
        self.send_command('SLS', params)

        raw_reply = self.receive(1024)
        
        time.sleep(20)

        self.send_command('CLS')

        return raw_reply
        #return self.decode_response(raw_reply, command)
