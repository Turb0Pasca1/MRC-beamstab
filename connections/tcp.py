# connections/tcp.py
import socket
from .base import BaseConnection

class TCPConnection(BaseConnection):
    def __init__(self, host: str, port: int, timeout=2):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def open(self):
        # socket.create_connection() is a wrapper of socket.connect() 
        self.sock = socket.create_connection(
            (self.host, self.port),
            timeout=self.timeout
        )

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def write(self, data: bytes):
        self.sock.sendall(data)

    def read(self, size: int) -> bytes:
        return self.sock.recv(size)