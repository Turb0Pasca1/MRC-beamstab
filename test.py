from connections import TCPConnection
from protocol import ProtocolDecoder  
import time

with TCPConnection('192.168.1.106', 2000) as conn:
    decoder = ProtocolDecoder(conn)
    #print(decoder.get_S1S())
    #for decoded in decoder.get_SLS(5,1):
    #   print(decoded)
    #decoder.get_SLS(5,1)
    # decoder.debug_message_stream()
    #print(decoder.get_error())
    print(decoder.get_S1S())