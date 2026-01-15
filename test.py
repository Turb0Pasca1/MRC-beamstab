from connections import TCPConnection
from protocol import ProtocolDecoder  

with TCPConnection('192.168.1.106', 2000) as conn:
    decoder = ProtocolDecoder(conn)
    decoded = decoder.get_position()
    print(decoded)