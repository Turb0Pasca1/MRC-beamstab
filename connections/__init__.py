# connections/__init__.py
from .tcp import TCPConnection
from .serial import SerialConnection

__all__ = ['TCPConnection', 'SerialConnection']