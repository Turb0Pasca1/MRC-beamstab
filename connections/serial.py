# connections/serial.py
from .base import BaseConnection

class SerialConnection(BaseConnection):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("SerialConnection not implemented yet")

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def write(self, data: bytes):
        raise NotImplementedError

    def read(self, size: int) -> bytes:
        raise NotImplementedError
