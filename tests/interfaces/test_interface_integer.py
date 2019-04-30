from Interfaces.IntegerInterface import IntegerInterface

def test_integer_interface_values():
    empty = IntegerInterface(0)
    assert empty.value == 0
    assert empty.bits(0, 1) == [0, 0]

    none = IntegerInterface(None)
    assert none.value == 0
    assert none.bits(0, 1) == [0, 0]
