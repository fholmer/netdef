from .DefaultInterface import DefaultInterface

class IntegerInterface(DefaultInterface):
    """ Interface som letter manipulering av bit i en integer """

    def __init__(self, value):
        """ Dersom verdi er none benytter vi i stedet 0 """
        super().__init__(value or 0) # integer: benytter 0 i stedet for None

    def bits(self, *offsets):
        "Returnerer liste med True eller False"
        return ([self.bit(offset) for offset in offsets])
    
    def bit(self, offset):
        "returnerer True eller False"
        return (self.value & (1 << offset) > 0)

    def setbit(self, offset, bit=True):
        """Endrer bit i verdi til True, kan også endre til False hvis bit=False
           Ingen returverdi."""
        if bit:
            self.value |= (1 << offset)
        else:
            self.clearbit(offset)

    def setbits(self, *offsets, bit=True):
        """Endrer bits i verdi til True, kan også endre til False hvis bit=False
           Ingen returverdi."""
        if bit:
            for offset in offsets:
                self.value |= (1 << offset)
        else:
            self.clearbits(*offsets)

    def clearbit(self, offset):
        """Endrer bit i verdi til False. Ingen returverdi."""
        self.value &= ~(1 << offset)

    def clearbits(self, *offsets):
        """Endrer bits i verdi til False. Ingen returverdi."""
        for offset in offsets:
            self.value &= ~(1 << offset)
