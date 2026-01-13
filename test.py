from connections import TCPConnection
from protocol import ProtocolDecoder  

with TCPConnection('192.168.1.106', 2000) as conn:
    decoder = ProtocolDecoder(conn)
    decoder.send_command(b'S1S;')
    raw_reply = decoder.receive(64)
    decoded = decoder.decode_response(raw_reply, 'S1S;')
    print(decoded)