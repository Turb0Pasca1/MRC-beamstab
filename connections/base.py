# connections/base.py
from abc import ABC, abstractmethod

class BaseConnection(ABC):
    '''
    abstract base class for all device connections
    '''

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def write(self, data: bytes):
        pass

    @abstractmethod
    def read(self, size: int) -> bytes:
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
