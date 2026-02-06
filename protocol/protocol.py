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

    def message_stream(self, size=1000) -> bytes:
        buffer = bytearray()

        while True:
            chunk = self.receive(size)
            if not chunk:
                raise ConnectionError('Server closed the connection')

            buffer.extend(chunk)

            while True:
                # print(buffer)
                # find message start marker
                start = buffer.find(b'\x00;')
                if start == -1:
                    start = buffer.find(b'\x01;')
                    if start == -1:
                        # raise ValueError('No response start marker found')
                        print('No response start marker found yet')
                
                # find message end marker
                end = buffer.find(b';', start + 3)
                if end == -1:
                    # raise ValueError('Incomplete response') 
                    print('Incomplete response, waiting for more data')

                # extract full message
                message = bytes(buffer[start:end + 1])

                # remove processed bytes from buffer
                del buffer[:end + 1]

                yield message

 
    ##### helper functions #####

    # debug controller behavior
    def plain_receive(self, size=100) -> bytes:
        #buffer = bytearray()

        while True:
            chunk = self.receive(size)
            if not chunk:
                raise ConnectionError('Server closed the connection')
            
            yield chunk

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
    
    def acknowledge(self, raw_reply: bytes) -> bool:
        """Check whether the command was correctly acknowledged by analyzing the raw response message.

        Interpret first two bytes of response (0;) as acknowledged message.
        Keyword arguments:
        raw_reply -- raw response of the controller (bytes)
        """
        if b'\x00;' in raw_reply:
            print('Command acknowledged')
            return True
        elif b'\x01;' in raw_reply:
            print('Error occurred')
            return False
        else:
            # there seems to be quite often the problem that the received reply is shorter than expected and
            # is missing the acknowledgment marker
            print('Number of bytes received as a reply:', len(raw_reply))
            print('Received reply:', raw_reply)
            raise ValueError('Command has not been acknowledged')        
        
    def reply_end(self, raw_reply: bytes) -> bool:
        """Check whether the response message ended correctly on (;).
        
        Keyword arguments:
        raw_reply -- raw response of the controller (bytes)
        """
        if raw_reply[-1] == 59:
            return True
        else:
            raise ValueError('Response did not end on ;')


    # decode response of a sent command    
    def decode_response(self, reply: bytes, command: str) -> dict:
        """Decode controller response message corresponding to a sent command.

        Decodes command response corresponding to COMMAND_RESPONSE_MAP
        Keyword arguments:
        reply   -- reply message of a send command by the controller (bytes)
        command -- command string that caused the return (str)
        return  -- dict of decoded response fields and values
        """
        # check command validity
        if command not in self.command_response_map:
            raise ValueError(f'Unknown command {command}')
        # extracts expected fields for the command
        fields = self.command_response_map[command]
        # build struct formatter string for unpacking the response
        fmt = self.get_formatter_str(fields)
        # check reply length with expected length
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
    
    ##### functions of MRC-communication protocol #####

    def get_S1S(self):
        """Start One Shot

        Send the S1S command to the controller to get a single measurement of the current state of the device
        and return the decoded response as a dictionary.
        return dict of
            StatusFlag,
            Res. Byte,
            DX1, DY1, DI1,
            DX2, DY2, DI2,
            RX1, RY1,
            RX2, RY2
        """
        command = 'S1S'
        self.send_command(command)
        fields = self.command_response_map[command]
        fmt = self.get_formatter_str(fields)
        length = struct.calcsize(fmt)
        raw_reply = self.receive(length)
        if (self.acknowledge(raw_reply)) and (self.reply_end(raw_reply)):
            return self.decode_response(raw_reply, command) 
        
    def get_error(self):
        command = 'GER'
        self.send_command(command)
        fields = self.command_response_map[command]
        fmt = self.get_formatter_str(fields)
        length = struct.calcsize(fmt)
        raw_reply = self.receive(length)
        print(raw_reply)
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
        duration = 5  

        n = 0
        for message in self.message_stream():
            print(message)
            #if (self.acknowledge(message)) and (self.reply_end(message)):
            #    yield self.decode_response(message, command)
            n += 1
            if n == m:
                break
        self.send_command('CLS') # change for function to check whether CLS was successful

            # stop after 20 seconds for continuesly measurement for now
            # if (time.time() - start_time >= duration):
            #     self.send_command('CLS') # change for function to check whether CLS was successful
            #     break


    def debug_message_stream(self):
        m = 5
        r = 1
        command = 'SLSmr'
        fields = ['m', 'r']
        fmt = self.get_formatter_str(fields, map=self.command_parameter_struct_map)
        params = struct.pack(fmt, m, r)
        self.send_command('SLS', params)
        l = 0
        for i in self.plain_receive():
            print(i)
            l+=len(i)
            print(l)
            if l >= m*25:
                break
        self.send_command('CLS')
        print(l)