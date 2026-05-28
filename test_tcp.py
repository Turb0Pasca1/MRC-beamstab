from connections import TCPConnection
from protocol import ProtocolDecoder  
import time

with TCPConnection('192.168.1.106') as conn:

    decoder = ProtocolDecoder(conn)
    print(decoder.start_one_shot())
    #print(decoder.get_drive_actuator())
    # print(decoder.get_error())
    '''
    for message in decoder.start_live_stream(5, 1):
        print(message)
    '''
    # decoder.clear_live_stream()