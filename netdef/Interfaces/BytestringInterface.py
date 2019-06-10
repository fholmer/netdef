from netdef.Interfaces.DefaultInterface import DefaultInterface

class ByteStringInterface(DefaultInterface):
    """ Interface som letter manipulering av bit i en integer """

    def __init__(self, value):
        """ Dersom verdi er none benytter vi i stedet 0 """
        super().__init__(value or b"")
