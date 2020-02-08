from netdef.Interfaces.FloatInterface import FloatInterface


def test_interface_values():
    empty = FloatInterface(0.0)
    assert empty.value == 0.0

    none = FloatInterface(None)
    assert none.value == 0.0

    one = FloatInterface(1.0)
    assert one.value == 1.0
