import datetime
from unittest.mock import Mock

from netdef.Sources import BaseSource


def test_basic_class():
    "test defaults"

    src = BaseSource.BaseSource()
    assert src.get_reference() == "C:None S:None K:None"
    assert src.value_as_string == "None"

    # interface for controllers
    assert src.pack_subitems("Something") is None
    assert src.can_unpack_subitems("") == False
    assert list(src.unpack_subitems("")) == [None]
    assert src.can_unpack_value("") == False
    assert src.unpack_value(1, 2, 3) == (1, 2, 3)
    assert src.pack_value(3) == (None, 3)
    assert src.pack_add_source() == False

    # values
    assert src.copy_value() is None
    assert src.copy_get_value() is None
    assert src.get is None
    assert src.set is None


def test_source_initial_value():
    "test source initial value"

    src = BaseSource.BaseSource(value=0)
    assert src.value_as_string == "0"

    # values
    assert src.copy_value() is 0
    assert src.copy_get_value() is None
    assert src.get is None
    assert src.set is None


def test_source_get_value():
    "test source get value"

    src = BaseSource.BaseSource()
    src.get = 111
    assert src.value_as_string == "111"

    # values
    assert src.copy_value() is 111
    assert src.copy_get_value() is 111
    assert src.get is 111
    assert src.set is None


def test_source_set_value():
    "test source set value"

    src = BaseSource.BaseSource()
    src.set = 222
    assert src.value_as_string == "222"

    # values
    assert src.copy_value() is 222
    assert src.copy_get_value() is None
    assert src.get is None
    assert src.set is 222


def test_source_copy_value():
    "test source copy value"

    get_val = [11]
    set_val = [22]

    src = BaseSource.BaseSource()
    src.get = get_val
    src.set = set_val
    assert src.value_as_string == "[22]"

    # check value identity. a copy should have a new identity
    assert src.get is get_val
    assert src.set is set_val
    assert src.copy_value() is not set_val
    assert src.copy_get_value() is not get_val
    assert src.copy_value() == set_val
    assert src.copy_get_value() == get_val


def test_source_reference():
    S = BaseSource.BaseSource
    # identical sources is not implemented overriding __hash__
    # we use .get_reference instead.

    # get_reference have to detect "identical" sources.
    src1 = S(key="key1", value="val1", controller="c1", source="s1", rule="r1")
    src2 = S(key="key1", value="val1", controller="c1", source="s1", rule="r1")
    assert src1.get_reference() == src2.get_reference()
    assert src1 is not src2

    # different rule still makes the same source
    src1 = S(key="key1", value="val1", controller="c1", source="s1", rule="r1")
    src2 = S(key="key1", value="val1", controller="c1", source="s1", rule="r2")
    assert src1.get_reference() == src2.get_reference()
    assert src1 is not src2

    # different value still makes the same source
    src1 = S(key="key1", value="val1", controller="c1", source="s1", rule="r1")
    src2 = S(key="key1", value="val2", controller="c1", source="s1", rule="r1")
    assert src1.get_reference() == src2.get_reference()
    assert src1 is not src2

    # key, controller or source makes .get_reference unique
    src1 = S(key="key1", value="val1", controller="c1", source="s1", rule="r1")
    src2 = S(key="key2", value="val1", controller="c1", source="s1", rule="r1")
    assert src1.get_reference() != src2.get_reference()
    assert src1 is not src2

    src1 = S(key="key1", value="val1", controller="c1", source="s1", rule="r1")
    src2 = S(key="key1", value="val1", controller="c2", source="s1", rule="r1")
    assert src1.get_reference() != src2.get_reference()
    assert src1 is not src2

    src1 = S(key="key1", value="val1", controller="c1", source="s1", rule="r1")
    src2 = S(key="key1", value="val1", controller="c1", source="s2", rule="r1")
    assert src1.get_reference() != src2.get_reference()
    assert src1 is not src2


def test_source_set_callback():
    src = BaseSource.BaseSource()
    _callable = Mock()
    src.register_set_callback(_callable)
    src.set = 444.42

    assert src.set_callback is _callable
    assert len(_callable.call_args[0]) == 3

    _src_cpy, _val, _stime = _callable.call_args[0]

    assert _src_cpy is src
    assert isinstance(_stime, datetime.datetime)
    assert _val == 444.42
