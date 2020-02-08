from netdef.Interfaces.CommTestInterface import CommTestInterface, Value


def test_interface_values():
    empty = CommTestInterface([0, False])
    assert isinstance(empty.value, Value)
    assert empty.value.delay == 0.0
    assert empty.value.available == False
    assert empty.available == False
    assert empty.delay == 0.0

    none = CommTestInterface(None)
    assert isinstance(none.value, Value)
    assert none.value.delay == 0.0
    assert none.value.available == False
    assert none.available == False
    assert none.delay == 0.0

    all_ok = CommTestInterface([0.2, True])
    assert isinstance(all_ok.value, Value)
    assert all_ok.value.available == True
    assert all_ok.value.delay == 0.2
    assert all_ok.available == True
    assert all_ok.delay == 0.2
