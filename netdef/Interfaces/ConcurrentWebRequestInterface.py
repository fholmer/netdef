from netdef.Interfaces.DefaultInterface import DefaultInterface

class Value():
    __slots__ = ("delay", "available", "data")
    def __init__(self, value):
        try:
            self.delay = float(value[0])
            self.available = bool(value[1])
            self.data = value[2]
            if self.data is None:
                self.data = {}
        except (IndexError, TypeError):
            self.delay = 0.0
            self.available = False
            self.data = {}

class ConcurrentWebRequestInterface(DefaultInterface):
    def __init__(self, value):
        super().__init__(Value(value))

    @property
    def available(self):
        return self.value.available
    
    @property
    def delay(self):
        return self.value.delay

    @property
    def data(self):
        return self.value.data
