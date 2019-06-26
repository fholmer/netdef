from .DefaultInterface import DefaultInterface

class IntegerInterface(DefaultInterface):
    """ Interface that facilitates bit manipulation in an integer """

    def __init__(self, value):
        "If value is none, we instead use 0"
        super().__init__(value or 0) # integer: benytter 0 i stedet for None

    def bits(self, *offsets):
        "Returns True or False List"
        return ([self.bit(offset) for offset in offsets])
    
    def bit(self, offset):
        "returns True or False"
        return (self.value & (1 << offset) > 0)

    def setbit(self, offset, bit=True):
        """Changing bit in value to True. Can also change to False if bit = False
            Does not return any value."""
        if bit:
            self.value |= (1 << offset)
        else:
            self.clearbit(offset)

    def setbits(self, *offsets, bit=True):
        """ Changing bits in value to True. Can also change to False if bit = False
            Does not return any value."""
        if bit:
            for offset in offsets:
                self.value |= (1 << offset)
        else:
            self.clearbits(*offsets)

    def clearbit(self, offset):
        "Changes bit in value to False. No return value."
        self.value &= ~(1 << offset)

    def clearbits(self, *offsets):
        "Changes bits in value to False. No return value."
        for offset in offsets:
            self.value &= ~(1 << offset)
