import serial
from .base import BaseConnection

class SerialConnection(BaseConnection):
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0):
        """
        Initializes the serial connection.
        Default baudrate is 115200 for USB-based systems.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def open(self):
        """
        Opens the serial port. 
        Note: Changed rtscts to False to bypass hardware handshaking 
        if the cable/adapter doesn't support it.
        """
        self.connection = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
            rtscts=False  # <--- CHANGE THIS FROM True TO False
        )

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.connection = None

    def write(self, data: bytes):
        """Sends ASCII command and binary parameters."""
        if self.connection:
            # Print for debugging: shows 'S1S;' and the hex values
            print(f"DEBUG [TX]: {data} | Hex: {data.hex(' ')}")
            self.connection.write(data)

    def read(self, size: int) -> bytes:
        """Reads binary-coded return values."""
        if self.connection:
            response = self.connection.read(size)
            # Print for debugging: shows what was received
            if response:
                print(f"DEBUG [RX]: {response} | Hex: {response.hex(' ')}")
            else:
                print(f"DEBUG [RX]: TIMEOUT (No data received)")
            return response
        return b""