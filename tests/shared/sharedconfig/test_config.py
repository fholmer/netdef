import os

import pytest

from netdef.Shared import SharedConfig
from netdef.Shared.SharedConfig import Config

PROJ = os.path.dirname(__file__)


def test_config_basic():

    # file not found
    with pytest.raises(ValueError):
        conf = Config("test", "..", "./tests/", "")

    # identifier is missing
    with pytest.raises(ValueError):
        conf = Config("test", "..", PROJ, "")

    # version is missing
    with pytest.raises(ValueError):
        conf = Config(
            "test",
            "..",
            PROJ,
            """
        [general]
        identifier = test
        """,
        )

    conf = Config(
        "test",
        "..",
        PROJ,
        """
    [general]
    identifier = test
    version = 1
    """,
    )

    assert conf.IDENTIFIER == "test"

    assert conf.config("install", "path") == ".."
    assert conf("install", "path") == ".."

    assert conf.config("proj", "path") == PROJ
    assert conf("proj", "path") == PROJ


def test_config_paths():
    conf = Config(
        "test",
        "",
        PROJ,
        """
    [general]
    identifier = test
    version = 1
    """,
    )

    assert conf("install", "path") == os.path.dirname(SharedConfig.__file__)
    assert conf("proj", "path") == PROJ


def test_config_config():
    conf = Config(
        "test",
        "..",
        PROJ,
        """
    [general]
    identifier = test
    version = 1
    """,
    )

    assert conf.config("new_section", "new_key", "no value") == "no value"

    conf.set_config("new_section", "new_key", "new value")
    assert conf.config("new_section", "new_key", "no value") == "new value"
    assert conf.get_dict("new_section") == {"new_key": "new value"}

    walk_res = list(conf.get_full_list())
    walk_res.sort()

    assert walk_res == [
        ("general", "identifier", "test"),
        ("general", "version", "1"),
        ("install", "path", ".."),
        ("new_section", "new_key", "new value"),
        ("proj", "path", PROJ),
    ]


def test_config_config_typecast():
    conf = Config(
        "test",
        "..",
        PROJ,
        """
    [general]
    identifier = test
    version = 1
    """,
    )

    assert conf("general", "version", 0) == 1
    assert conf("general", "version", 0.0) == 1.0
    assert conf("general", "version", False) == True
    assert conf("general", "version", "") == "1"
    assert conf("general", "version", None) == "1"
    assert conf("general", "version", []) == ["1"]
    assert conf("general", "version", ()) == ("1",)


def test_config_config_internal_cache():
    conf = Config(
        "test",
        "..",
        PROJ,
        """
    [general]
    identifier = test
    version = 1
    """,
    )

    # no cache
    assert conf.config("section1", "key1", "first", False) == "first"
    assert conf.config("section1", "key1", "second", False) == "second"

    # with cache (the default)
    assert conf.config("section2", "key2", "first", True) == "first"
    assert conf.config("section2", "key2", "second", True) == "first"
