from .DefaultInterface import DefaultInterface

class Value():
    __slots__ = ("delay", "available")
    def __init__(self, value):
        try:
            self.delay = value[0]
            self.available = value[1]
        except (IndexError, TypeError):
            self.delay = 0.0
            self.available = False

class CommTestInterface(DefaultInterface):
    def __init__(self, value):
        super().__init__(Value(value))

    @property
    def available(self):
        return self.value.available
    
    @property
    def delay(self):
        return self.value.delay
