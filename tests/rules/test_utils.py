import pytest
from netdef.Rules import utils
import os.path

def test_import_abs_module_string():
    mod = utils.get_module_from_string("os.path", "", "", "", "")
    assert mod is os.path

def test_import_rel_module_string():
    mod = utils.get_module_from_string(".path", "os", "", "", "")
    assert mod is os.path

def test_import_rel_filepath_1():
    mod = utils.get_module_from_string(
        "./tests/rules/expression_simple.py",
        "",
        "",
        "tests",
        "expression_simple"
    )
    assert mod.__file__ == os.path.abspath("./tests/rules/expression_simple.py")

def test_import_rel_filepath_2():
    mod = utils.get_module_from_string(
        "./expression_simple.py",
        "",
        os.path.abspath("./tests/rules"),
        "tests",
        "expression_simple"
    )
    assert mod.__file__ == os.path.abspath("./tests/rules/expression_simple.py")

def test_import_abs_filepath():
    mod = utils.get_module_from_string(os.path.abspath(
        "tests/rules/expression_simple.py"),
        "",
        "",
        "tests",
        "expression_simple"
    )
    assert mod.__file__ == os.path.abspath("./tests/rules/expression_simple.py")

def test_missing_location_name():
    with pytest.raises(ValueError):
        utils.get_module_from_string("./tests/rules/expression_simple.py", "", "", "", "")

def test_missing_mod_name():
    with pytest.raises(ValueError):
        utils.get_module_from_string("./tests/rules/expression_simple.py", "", "", "tests", "")

def test_missing_file_not_found():
    with pytest.raises(ValueError):
        utils.get_module_from_string("./expression_simple.py", "", "", "tests", "expression_simple")

def test_missing_module_not_found():
    with pytest.raises(ModuleNotFoundError):
        utils.get_module_from_string("path", "sys", "", "", "")

def test_missing_package_not_found():
    with pytest.raises(TypeError):
        utils.get_module_from_string(".path", "", "", "", "")
