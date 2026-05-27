# connections/tcp.py
import socket
from .base import BaseConnection

class TCPConnection(BaseConnection):
    def __init__(self, host: str, port: int = 2000, timeout: float = 2.0):
        """Initializes the TCP/IP connection for the MRC beam stabilization system.
        
        Port 2000 is default for ETH-based systems.
        
        :param host: IP-address.
        :param port: The port.
        :param timeout: Read timeout in seconds.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def open(self):
        """Opens the TCP/IP connection."""
        
        # socket.create_connection() is a wrapper of socket.connect() 
        self.sock = socket.create_connection(
            (self.host, self.port),
            timeout=self.timeout
        )

    def close(self):
        """Closes the TCP/IP connection."""
        if self.sock:
            self.sock.close()
            self.sock = None

    def write(self, data: bytes):
        """Sends uppercase ASCII command names and binary-coded parameters[cite: 9, 11]."""
        if self.sock:
            self.sock.sendall(data)

    def read(self, size: int) -> bytes:
        """Reads binary-coded return values[cite: 12]."""
        if self.sock:
            return self.sock.recv(size)
        return b""