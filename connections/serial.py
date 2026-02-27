import serial
from .base import BaseConnection

class SerialConnection(BaseConnection):
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0, rtscts: bool = False):
        """
        Initializes the serial connection for the MRC beam stabilization system.
        
        Default baudrate is 115200 for USB-based systems. 
        Baudrate 460800 is default for ETH-based systems.
        
        :param port: The COM port (e.g., 'COM5' on Windows or '/dev/ttyUSB0' on Linux).
        :param baudrate: Transmission speed (115200, 460800, or 921600).
        :param timeout: Read timeout in seconds.
        :param rtscts: Enable hardware handshaking. While the manual specifies 
                       8-N-1-CTS-RTS, many USB-to-serial adapters require 
                       this to be False to function correctly.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.rtscts = rtscts
        self.connection = None

    def open(self):
        """
        Opens the serial port with 8 data bits, no parity, and one stop bit (8-N-1).
        """
        self.connection = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
            rtscts=self.rtscts
        )

    def close(self):
        """Closes the serial connection if it is open."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.connection = None

    def write(self, data: bytes):
        """
        Sends uppercase ASCII command names and binary-coded parameters[cite: 9, 11].
        """
        if self.connection:
            self.connection.write(data)

    def read(self, size: int) -> bytes:
        """
        Reads binary-coded return values[cite: 12].
        """
        if self.connection:
            return self.connection.read(size)
        return b""