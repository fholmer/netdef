from .DefaultInterface import DefaultInterface

class FloatInterface(DefaultInterface):

    def __init__(self, value):
        super().__init__(value or 0.0)
