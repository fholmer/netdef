from .DefaultInterface import DefaultInterface

class NoUnitInterface(DefaultInterface):
    def get_value_and_unit(self):
        return str(self.value)

class ByteUnitInterface(DefaultInterface):
    def __init__(self, value):
        super().__init__(value or 0)

    def get_value_and_unit(self):
        return bytes2human(self.value)

class PercentUnitInterface(DefaultInterface):
    def __init__(self, value):
        super().__init__(value or 0.0)

    def get_value_and_unit(self):
        return "{}%".format(round(self.value, 1))

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n
