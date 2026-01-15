# protocol/defs.py

# https://www.mrc-systems.de/downloads/de/laser-strahlstabilisierung/BA-digital-communication-interface_ver8_2.pdf (24.05.2023)

# dict of command parameters and respective dtypes for struct
COMMAND_PARAMETER_STRUCT_MAP = {
    'm': 'H',            # Number of data blocks to be transmitted in a live stream (1-65500, 0=endless)
    'r': 'H',            # Sampling rate for data blocks in samples/s (1 – 500 samples/s)
    's': 'B',            # Stage number to be selected (1 = stage1, 2 = stage2, 3 = both (only for software trigger commands (STFs; , CTFs;)))
    'p': 'H',            # P-factor of control loop (0 – 5000mV)
    'o': 'h',            # Offset for target position on detector (-5000mV – +5000mV)
    'a': 'B',            # Axis to be selected (“x” (0x78) or “y” (0x79))
    'd': 'h',            # Drive value for direct piezo positioning (-5000mV – +5000mV)
    'b': 'B',            # Baudrate (1 = 115200 bit/s, 4 = 460800 bit/s, 9 = 921600 bit/s)
    'l': 'B',            # User defined label for the beam stabilization system (max length: 25 ASCII characters) in [] brackets
    'i': 'H'             # Detector sensitivity (0 – 5000mV)
}

# dict of possible return values and respective dtypes for struct
RETURN_VALUE_STRUCT_MAP = {
    'A1': 'B',           # unsigned char    # Stabilization of stage1 active or not active, 1 = active, 0 = not active
    'A2': 'B',           # unsigned char    # Stabilization of stage2 active or not active, 1 = active, 0 = not active
    'OnOff1': 'B',       # unsigned char    # Stabilization of stage1 enabled or disabled, 1 = enabled, 0 = disabled
    'OnOff2': 'B',       # unsigned char    # Stabilization of stage2 enabled or disabled, 1 = enabled, 0 = disabled
    'StatusFlag': 'B',   # unsigned char    # Encoded status byte of current system state (see Fig. 3)
    'DX1': 'h',          # short            # Detector1, beam position on x-axis (-5000mV – +5000mV)
    'DY1': 'h',          # short            # Detector1, beam position on y-axis (-5000mV – +5000mV)
    'DI1': 'H',          # unsigned short   # Detector1, intensity (0 – 8000mV)
    'DX2': 'h',          # short            # Detector2, beam position on x-axis (-5000mV – +5000mV)
    'DY2': 'h',          # short            # Detector2, beam position on y-axis (-5000mV – +5000mV)
    'DI2': 'H',          # unsigned short   # Detector2, intensity (0 – 8000mV)
    'RX1': 'H',          # unsigned short   # Piezo range of x-axis, stage1 (0 – 10000mV)
    'RY1': 'H',          # unsigned short   # Piezo range of y-axis, stage1 (0 – 10000mV)
    'RX2': 'H',          # unsigned short   # Piezo range of x-axis, stage2 (0 – 10000mV)
    'RY2': 'H',          # unsigned short   # Piezo range of y-axis, stage2 (0 – 10000mV)
    'p': 'H',            # unsigned short   # P-factor of control loop (0 – 5000mV)
    'o': 'h',            # short            # Offset for target position on detector (-5000mV – +5000mV)
    'd': 'h',            # short            # Drive Actuator values (-5000mV – +5000mV)
    'dx1': 'h',                             # Drive Actuator values stage1 x
    'dy1': 'h',                             # Drive Actuator values stage1 y
    'dx2': 'h',                             # Drive Actuator values stage2 x
    'dy2': 'h',                             # Drive Actuator values stage2 y
    'l': '25s',          # 25 byte          # User defined label for the beam stabilization system (max length: 25 ASCII characters) in [] brackets
    'Device_id': '47s',  # 47 byte          # Unique device id, length: 47 byte
    'CMD': '3s',         # 3 byte           # Name of the command that provoked the last error, length: 3 byte
    'e': 'c',            # char             # Error code
    'i': 'H',            # unsigned short   # Detector sensitivity (0 – 5000mV)
    'ResByte': 'B',      # unsigned char?
    'fe': 'B',           # unsigned char    # 0 no error, 1 error
    'semi_fe': 'B',      # unsigned char?   # ;
    'semi_end': 'B'      # unsigned char?   # ;
}

# keys to interpret as ascii
ASCII_KEYS = {'Device_id', 'l', 'CMD'}

# command response structure 
COMMAND_RESPONSE_MAP = {
    'StatusFlag': [     # bitwise interpretation necessary 
        'EF',           # End of Stream Flag: nidicates the last stream package of SLS-command (always zero except in last stream package)
        'A2',           # stage2 active (1) or inactive (0)
        'A1',           # stage1 active (1) or inactive (0)
        'OnOff2',       # stage2 enabled (1) or disabled (0)
        'OnOff1',       # stage1 enabled (1) or disabled (0)
        'Adj2',         # stage2 adjust function set for software (1) or external signal (0)
        'Adj1',         # stage1 adjust function set for software (1) or external signal (0)
        'PF'            # p-factor function is set for software (1) or external signal (0)
    ],
    'S1S': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'StatusFlag', 
        'ResByte',   
        'DX1', 'DY1', 'DI1',     
        'DX2', 'DY2', 'DI2',      
        'RX1', 'RY1',              
        'RX2', 'RY2',              
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'SLSmr': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'StatusFlag', 
        'ResByte',   
        'DX1', 'DY1', 'DI1',     
        'DX2', 'DY2', 'DI2',      
        'RX1', 'RY1',              
        'RX2', 'RY2',              
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'SPSm': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'StatusFlag', 
        'ResByte',   
        'DX1', 'DY1', 'DI1',     
        'DX2', 'DY2', 'DI2',      
        'RX1', 'RY1',              
        'RX2', 'RY2',              
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'CLS': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'SSHs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'CSHs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'SPFsp': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
    ],
    'GPFs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'p',
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'SAIsao': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
    ],
    'GAIsa': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'o',
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'GPFs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'SDAsad': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'GDA': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'dx1', 'dy1', 
        'dx2', 'dy2',
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'SDSsi': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'GDSs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'i'
    ],
    'SEAs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'CEAs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'GEA': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'OnOff1',
        'OnOff2',
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'STFs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'CTFs': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'SHS': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'CHS': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'SBRb': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'GSF': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'StatusFlag',
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'GID': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'Device_id',
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'SLAI': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe'       # semicolon (ascii value 59 (0x3b))
    ],
    'GLA': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'l',
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ],
    'GER': [
        'fe',           # error acknowledge: no error (0), error (1)
        'semi_fe',      # semicolon (ascii value 59 (0x3b))
        'CMD',
        'e',
        'semi_end'      # semicolon (ascii value 59 (0x3b))
    ]
}

ERROR_CODE_MAP = {
    0x00: 'No error occurred since startup',
    0xFF: 'Command not recognized',
    0xFE: 'Parameter out of range',
    0xFD: 'Wrong command length',
    0xFC: 'Stream is running',
    0xFB: 'Stage is enabled',
    0xFA: 'Stage is disabled',
    0xF9: 'Stream is not running',
    0xF8: 'ADDA functions unavailable',
    0xF7: 'Receive buffer overflow',
    0xF6: 'Baudrate not changeable',
}

ERROR_DESCRIPTION_MAP = {
    0x00: (
        'The error code is only updated after an error occurred. '
        'Hence the error code is not reset to 0 when a function was called that did not provoke an error. '
        'Error code 0 is just the default value after startup.'
    ),
    0xFF: (
        'The received command name does not match any of the specified commands. '
        'This is also the case if lowercase letters are sent instead of uppercase letters.'
    ),
    0xFE: (
        'Please concern to section 2 for the allowed values of the parameters. '
        'If the parameters are in the specified range it could mean that they were sent as ASCII characters '
        'when hex numbers are needed or vice versa.'
    ),
    0xFD: (
        'This error code is set when a function was called with parameters that does not expect parameters. '
        'Calling a function that does expect parameters can also provoke this error code when the parameters sent exceed '
        'the specified length in byte (i.e. short was sent when char should have been sent). '
        'Note: If the total received bytes exceed 30, the error code -9 (Receive buffer overflow) is set.'
    ),
    0xFC: (
        'After starting the stream with SLS or SPS no other command than CLS can be called. '
        'CLS will stop the stream and after that, other functions can be called. '
        'Remark: Calling GER while the stream is running will also set this error code. '
        'To investigate the error calling CLS to stop the stream is necessary first.'
    ),
    0xFB: (
        'This error code is set when a function is called that needs a disabled stage '
        'while the concerning stage is enabled.'
    ),
    0xFA: (
        'This error code is set when a function is called that needs an enabled stage '
        'while the concerning stage is disabled.'
    ),
    0xF9: (
        'Calling CLS while no stream is running will set this error code.'
    ),
    0xF8: (
        'This error code is set on Basic systems after trying to call a function that needs the optional ADDA-module. '
        'This concerns the commands SPS, CTF and STF. '
        'Note: The label on the backside of the controller indicates whether the system is equipped with an ADDA-module or not. '
        'In addition, the Device_Id returned by GID contains "AD-DA" for systems with an ADDA-module and "Basic" for those without.'
    ),
    0xF7: (
        'The receive buffer can hold up to 30 byte. '
        'When the system receives more than 30 byte without a semicolon in between, the buffer will overflow and this error code will be set.'
    ),
    0xF6: (
        'It is not possible to change the baudrate for systems that are equipped with an Ethernet module. '
        'This concerns the command SBR.'
    ),
}
