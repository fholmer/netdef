from .DefaultInterface import DefaultInterface

class StringInterface(DefaultInterface):

    def __init__(self, value):
        super().__init__(value or "")
