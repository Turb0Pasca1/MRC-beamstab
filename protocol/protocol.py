# protocol/protocol.py

from .defs import (
    COMMAND_PARAMETER_STRUCT_MAP,
    COMMAND_RESPONSE_MAP,
    RETURN_VALUE_STRUCT_MAP,
    ASCII_KEYS,ERROR_CODE_MAP,
    ERROR_DESCRIPTION_MAP
)
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
        command: command to send of dtype str
        params: parameter to send with the command of dtype byte
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
    
    def plain_receive(self, size=100):
        '''
        Docstring for plain_receive

        listens to TCP data stream and yields the received bytes to be worked with
        '''
        while True:
            chunk = self.receive(size)
            if not chunk:
                raise ConnectionError('Server closed the connection')
            
            yield chunk

    def message_single(self, length):
        buffer = bytearray()
        for chunk in self.plain_receive():
            buffer.extend(chunk)
            if len(buffer) >= length:
                break
        return bytes(buffer[:length])

    def message_stream(self, size=1000):
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
            #print('Command acknowledged')
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
        raw_reply = self.message_single(length)
        if (self.acknowledge(raw_reply)) and (self.reply_end(raw_reply)):
            return self.decode_response(raw_reply, command) 
        
    def get_GDA(self):
        """Get Drive Actuator values.

        Send the GDA command to the controller to read the current piezo
        actuator drive voltages for all axes and return the decoded response.

        return dict of
            dx1, dy1  -- Stage-1 actuator drive values (-5000mV – +5000mV)
            dx2, dy2  -- Stage-2 actuator drive values (-5000mV – +5000mV)
        """
        command = 'GDA'
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

    ##### Stage 2 reference positioning and stabilization #####

    def set_reference_position(self, offset_x: int, offset_y: int, stage: int = 2) -> dict:
        """Set a reference target position on the detector for stage 2 by applying
        X and Y offsets via the SAIsao command.

        The offset shifts the closed-loop stabilization target away from the detector
        centre (0mV). Positive and negative values are both valid.

        Parameters
        ----------
        offset_x : int
            Target offset on the x-axis in mV (-5000 – +5000).
        offset_y : int
            Target offset on the y-axis in mV (-5000 – +5000).
        stage : int
            Stage number (default 2). Must be 1 or 2; 3 is only valid for
            trigger commands and is therefore rejected here.

        Returns
        -------
        dict
            {'x': decoded SAIsao response, 'y': decoded SAIsao response}

        Raises
        ------
        ValueError
            If stage is not 1 or 2, or if offsets are outside ±5000 mV.
        """
        if stage not in (1, 2):
            raise ValueError(f'stage must be 1 or 2, got {stage}')
        if not (-5000 <= offset_x <= 5000):
            raise ValueError(f'offset_x must be between -5000 and +5000 mV, got {offset_x}')
        if not (-5000 <= offset_y <= 5000):
            raise ValueError(f'offset_y must be between -5000 and +5000 mV, got {offset_y}')

        results = {}
        for axis_char, offset in (('x', offset_x), ('y', offset_y)):
            axis_key = 'x'  # label for result dict

            command = 'SAIsao'
            param_fields = ['s', 'a', 'o']
            fmt = self.get_formatter_str(param_fields, map=self.command_parameter_struct_map)

            # axis encoded as ASCII byte value: x = 0x78, y = 0x79
            axis_byte = ord(axis_char)
            params = struct.pack(fmt, stage, axis_byte, offset)
            self.send_command('SAI', params)

            response_fields = self.command_response_map[command]
            response_fmt    = self.get_formatter_str(response_fields)
            length          = struct.calcsize(response_fmt)
            raw_reply       = self.receive(length)

            if self.acknowledge(raw_reply) and self.reply_end(raw_reply):
                results[axis_char] = self.decode_response(raw_reply, command)

        return results

    def enable_stabilization(self, stage: int = 2) -> dict:
        """Enable closed-loop stabilization on the given stage via SEAs.

        Parameters
        ----------
        stage : int
            Stage number to enable (default 2).

        Returns
        -------
        dict
            Decoded SEAs response.
        """
        command = 'SEAs'
        param_fields = ['s']
        fmt    = self.get_formatter_str(param_fields, map=self.command_parameter_struct_map)
        params = struct.pack(fmt, stage)
        self.send_command('SEA', params)

        response_fields = self.command_response_map[command]
        response_fmt    = self.get_formatter_str(response_fields)
        length          = struct.calcsize(response_fmt)
        raw_reply       = self.receive(length)

        if self.acknowledge(raw_reply) and self.reply_end(raw_reply):
            return self.decode_response(raw_reply, command)

    def disable_stabilization(self, stage: int = 2) -> dict:
        """Disable closed-loop stabilization on the given stage via CEAs.

        Parameters
        ----------
        stage : int
            Stage number to disable (default 2).

        Returns
        -------
        dict
            Decoded CEAs response.
        """
        command = 'CEAs'
        param_fields = ['s']
        fmt    = self.get_formatter_str(param_fields, map=self.command_parameter_struct_map)
        params = struct.pack(fmt, stage)
        self.send_command('CEA', params)

        response_fields = self.command_response_map[command]
        response_fmt    = self.get_formatter_str(response_fields)
        length          = struct.calcsize(response_fmt)
        raw_reply       = self.receive(length)

        if self.acknowledge(raw_reply) and self.reply_end(raw_reply):
            return self.decode_response(raw_reply, command)

    def debug_message_stream(self):
        m = 1
        r = 500
        command = 'SLSmr'
        fields = ['m', 'r']
        fmt = self.get_formatter_str(fields, map=self.command_parameter_struct_map)
        params = struct.pack(fmt, m, r)
        self.send_command('SLS', params)
        #getting_chunks = self.plain_receive()
        buffer = bytearray()
        for chunk in self.plain_receive():
            buffer.extend(chunk)
            if len(buffer) >= 25:
                break
        self.send_command('CLS')
        

    def set_p_factor(self, stage: int, p: int) -> dict:
        """Set the P-factor of the control loop via SPFsp.

        Parameters
        ----------
        stage : int
            Stage number to set P-factor for (1 or 2).
        p : int
            P-factor value in mV (0 - 5000).

        Returns
        -------
        dict
            Decoded SPFsp response.

        Raises
        ------
        ValueError
            If stage is not 1 or 2, or if p is outside 0 - 5000 mV.
        """
        if stage not in (1, 2):
            raise ValueError(f'stage must be 1 or 2, got {stage}')
        if not (0 <= p <= 5000):
            raise ValueError(f'p must be between 0 and 5000 mV, got {p}')

        command = 'SPFsp'
        param_fields = ['s', 'p']
        fmt    = self.get_formatter_str(param_fields, map=self.command_parameter_struct_map)
        params = struct.pack(fmt, stage, p)
        self.send_command('SPF', params)

        response_fields = self.command_response_map[command]
        response_fmt    = self.get_formatter_str(response_fields)
        length          = struct.calcsize(response_fmt)
        raw_reply       = self.receive(length)

        if self.acknowledge(raw_reply) and self.reply_end(raw_reply):
            return self.decode_response(raw_reply, command)

    def get_p_factor(self, stage: int) -> dict:
        """Read the current P-factor of the control loop via GPFs.

        Parameters
        ----------
        stage : int
            Stage number to query (1 or 2).

        Returns
        -------
        dict
            Decoded GPFs response, including 'p' (0 - 5000 mV).

        Raises
        ------
        ValueError
            If stage is not 1 or 2.
        """
        if stage not in (1, 2):
            raise ValueError(f'stage must be 1 or 2, got {stage}')

        command = 'GPFs'
        param_fields = ['s']
        fmt    = self.get_formatter_str(param_fields, map=self.command_parameter_struct_map)
        params = struct.pack(fmt, stage)
        self.send_command('GPF', params)

        response_fields = self.command_response_map[command]
        response_fmt    = self.get_formatter_str(response_fields)
        length          = struct.calcsize(response_fmt)
        raw_reply       = self.receive(length)

        if self.acknowledge(raw_reply) and self.reply_end(raw_reply):
            return self.decode_response(raw_reply, command)
