# protocol/protocol.py

from .defs import *
import struct

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

    def send_command(self, command: str, params: bytes | None):
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
    def get_formatter_str(self, fields)
        # build struct format string
        # high byte first
        fmt = '>'  
        for field in fields:
            if field not in self.return_value_struct_map:
                raise ValueError(f'Field {field} not in return_value_struct_map')
            fmt += self.return_value_struct_map[field]
        return fmt

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
        result = dict(zip(fields, unpacked))
    
        # handle special cases of keys
        for key, val in result.items():
            # StatusFlag: convert to bit dictionary
            if key == 'StatusFlag':
                bits = format(val, '08b')
                result['StatusFlag'] = dict(zip(self.command_response_map.get('StatusFlag', []), bits))
                continue
    
            # decode fields received as ascii
            if key in self.ascii_keys:
                if isinstance(val, (bytes, bytearray)):
                    result[key] = val.rstrip(b'\x00').decode('ascii')
                elif isinstance(val, int) and 0 <= val <= 127:
                    result[key] = chr(val)
                continue
    
            # map error code
            if key == 'e':
                code = val
                if isinstance(code, (bytes, bytearray)) and len(code) == 1:
                    code = code[0]
    
                error_name = self.error_code_map.get(code, f'UnknownError_0x{code:02X}')
                error_description = self.error_description_map.get(code, 'No description available.')
    
                result['e'] = {
                    'ErrorCode': f'0x{code:02X}',
                    'ErrorName': error_name,
                    'ErrorDescription': error_description
                }
                continue
    
        return result
    
    def get_position(self):
        command = 'S1S'
        self.send_command(command)
        fields = self.command_response_map[command]
        fmt = self.get_formatter_str(fields)
        length = struct.calcsize(fmt)
        raw_reply = self.receive(length)
        return self.decode_response(raw_reply, command)

