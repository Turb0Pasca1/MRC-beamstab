from connections import TCPConnection
from protocol import ProtocolDecoder  
import time

with TCPConnection('192.168.1.106') as conn:

    decoder = ProtocolDecoder(conn)
    print(decoder.get_S1S())
    print(decoder.get_GDA())
    print(decoder.get_GER())
