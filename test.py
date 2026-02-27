from connections import TCPConnection
from connections.serial import SerialConnection
from protocol import ProtocolDecoder  

with SerialConnection('COM5') as conn:
    decoder = ProtocolDecoder(conn)
    print(decoder.get_S1S())
    #for decoded in decoder.get_SLS(5,1):
    #    print(decoded)
    #decoder.get_SLS(5,1)
    # decoder.debug_message_stream()