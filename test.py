from connections import TCPConnection
from protocol import ProtocolDecoder  

with TCPConnection('192.168.1.106', 2000) as conn:
    decoder = ProtocolDecoder(conn)
    for decoded in decoder.get_SLS(3,1):
        print(decoded)