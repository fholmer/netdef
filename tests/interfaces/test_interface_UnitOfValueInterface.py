from netdef.Interfaces import UnitOfValueInterface


def test_interface_NoUnitInterface():
    empty = UnitOfValueInterface.NoUnitInterface(0.0)
    assert empty.value == 0.0

    none = UnitOfValueInterface.NoUnitInterface(None)
    assert none.value == None #  ...

    one = UnitOfValueInterface.NoUnitInterface(1.0)
    assert one.value == 1.0

def test_interface_ByteUnitInterface():
    empty = UnitOfValueInterface.ByteUnitInterface(0)
    assert empty.value == 0
    assert empty.get_value_and_unit() == "0B"

    none = UnitOfValueInterface.ByteUnitInterface(None)
    assert none.value == 0
    assert none.get_value_and_unit() == "0B"

    big = UnitOfValueInterface.ByteUnitInterface(65432)
    assert big.value == 65432
    assert big.get_value_and_unit() == "63.9K"

def test_interface_PercentUnitInterface():
    empty = UnitOfValueInterface.PercentUnitInterface(0.0)
    assert empty.value == 0.0
    assert empty.get_value_and_unit() == "0.0%"

    none = UnitOfValueInterface.PercentUnitInterface(None)
    assert none.value == 0.0
    assert none.get_value_and_unit() == "0.0%"

    one = UnitOfValueInterface.PercentUnitInterface(1.0)
    assert one.value == 1.0
    assert one.get_value_and_unit() == "1.0%"

    half = UnitOfValueInterface.PercentUnitInterface(50)
    assert half.value == 50
    assert half.get_value_and_unit() == "50%"

    pi = UnitOfValueInterface.PercentUnitInterface(3.14)
    assert pi.value == 3.14
    assert pi.get_value_and_unit() == "3.1%"
