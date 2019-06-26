from .DefaultInterface import DefaultInterface

class ByteStringInterface(DefaultInterface):

    def __init__(self, value):
        super().__init__(value or b"")
