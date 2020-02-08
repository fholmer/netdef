import pytest

from netdef.Interfaces.IntegerInterface import IntegerInterface


def test_integer_interface_values():
    empty = IntegerInterface(0)
    assert empty.value == 0
    assert empty.bits(0, 1) == [0, 0]
    assert empty.bit(0) == False

    none = IntegerInterface(None)
    assert none.value == 0
    assert none.bits(0, 1) == [0, 0]
    assert none.bit(0) == False

    one = IntegerInterface(1)
    assert one.value == 1
    assert one.bits(0, 1) == [1, 0]
    assert one.bit(0) == True


def test_integer_interface_setbit():
    empty = IntegerInterface(0)
    empty.setbit(0)
    assert empty.value == 1

    empty.setbit(1)
    assert empty.value == 3

    tree = IntegerInterface(3)
    tree.setbit(0, False)
    assert tree.value == 2

    tree.setbit(1, False)
    assert tree.value == 0


def test_integer_interface_setbits():
    empty = IntegerInterface(0)
    empty.setbits(0)
    assert empty.value == 1

    empty.setbits(1, 2)
    assert empty.value == 7

    seven = IntegerInterface(7)
    seven.setbits(2, bit=False)
    assert seven.value == 3

    seven.setbits(0, 1, bit=False)
    assert seven.value == 0

    with pytest.raises(TypeError):
        seven.setbits([0, 1], bit=False)


def test_integer_interface_clearbit():
    seven = IntegerInterface(7)
    seven.clearbit(2)
    assert seven.value == 3

    seven.clearbit(0)
    assert seven.value == 2

    seven.clearbit(1)
    assert seven.value == 0


def test_integer_interface_clearbit():
    seven = IntegerInterface(7)
    seven.clearbits(0, 2)
    assert seven.value == 2

    seven.clearbits(1)
    assert seven.value == 0
