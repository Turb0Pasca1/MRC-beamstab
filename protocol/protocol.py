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
        '''
        Docstring for send_command

        sends command to the device
        command: command to send of dytpe str
        params: parameter to send with the command of dytpe byte
        '''
        if params is None:
            params = b''
        if not isinstance(command, str):
            raise TypeError('Command must be of dtype str')
        if not isinstance(params, (bytes, bytearray)):
            raise TypeError('Params must be of dtype bytes')
        block = (
            command.encode('ascii') +
            params +
            b';'
        )
        self.connection.write(block)

    def receive(self, size: int) -> bytes:
        '''
        Docstring for receive
        
        receives data of size size
        '''
        return self.connection.read(size)
    
    def receive_continuesly(self) -> bytes:
        '''
        Docstring for receive_continuesly
        
        calls receive in a loop to receive data of livestreams
        '''
        while True:
            # receive arbitary amount (1024) of bytes in each chunk
            chunk = self.receive(1014)
            if not chunk:
                raise ConnectionError('Server closed the connection')
            yield chunk
 
    ##### helper functions #####

    def get_formatter_str(self, fields, map=None):
        '''
        Docstring for get_fromatter_str

        builder for struct formatter string to pack and unpack bytes
        fields: fields of defs.py containing the dytpe information of parameters to send and attributes to receive
        map:    dict to map the fields onto
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
    
    def acknowledge(self, reply: bytes):
        '''
        Docstring for acknowledge
        ToDo: change to find '0;' in encoded message to choose whether to decode or not

        interpret first two bytes of response (0;) as acknowledged message
        reply: raw response of the controller
        '''
        # if (response['fe'] == 0) & (response['semi_fe'] == 59):
        #     return True
        # else:
        #     return False

        if b'\x00;' in reply:
            print('Command acknowledged')
            return True
        elif b'\x01;' in reply:
            print('Error occurred')
            # add automatic send command to get error message
            return False
        else:
            raise ValueError('Command has not been acknowledged')
        
    def reply_end(self, reply: bytes):
        '''
        Docstring for reply_end
        
        check whether the resonse message ended correctly
        reply: raw response of the controller
        '''

        if reply[-1] == 59:
            return True
        else:
            raise ValueError('Response did not end on ;')


    # decode response of a sent command    
    def decode_response(self, reply: bytes, command: str):
        '''
        Docstring of decode_response

        decodes command response corresponding to COMMAND_RESPONSE_MAP
        reply: reply message of a send command by the controller
        command: command string that caused the return
        return dict of command return keys and values
        '''
        # check command validity
        if command not in self.command_response_map:
            raise ValueError(f'Unknown command {command}')
    
        fields = self.command_response_map[command]
    
        fmt = self.get_formatter_str(fields)

        # check reply length with expected length
        # add to re-send the command
        if struct.calcsize(fmt) != len(reply):
            raise ValueError(f'Length of reply {len(reply)} byte does not match length of expected "{command}" length of {struct.calcsize(fmt)} byte.')
          
        # unpack
        unpacked = struct.unpack(fmt, reply)
        response = dict(zip(fields, unpacked))
    
        # handle special cases of keys
        for key, val in response.items():
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
    
    def get_S1S(self):
        command = 'S1S'
        self.send_command(command)
        fields = self.command_response_map[command]
        fmt = self.get_formatter_str(fields)
        length = struct.calcsize(fmt)
        raw_reply = self.receive(length)
        if (self.acknowledge(raw_reply)) and (self.reply_end(raw_reply)):
            return self.decode_response(raw_reply, command) 
    
    def get_SLS(self, m, r):
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
        params = struct.pack(fmt, m, r)
        self.send_command('SLS', params)

        start_time = time.time()
        duration = 20  

        for chunk in self.receive_continuesly():
            print(chunk)

            # stop after 20 seconds for continuesly measurement for now
            if (m == 0) and (time.time() - start_time >= duration):
                self.send_command('CLS') # change for function to check whether CLS was successful
                break
