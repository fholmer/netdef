from netdef.testutils import MockExpression
from netdef.Sources.InternalSource import InternalSource
from first_app.Sources.SubprocessSource import SubprocessSource

def test_hello():
    mock = MockExpression(
        module="config/command_rule.py",
        intern=InternalSource("generic"),
        cmd=SubprocessSource("echo hello")
    )
    mock.intern.update_value(None, stat_init=True)
    mock.cmd.assert_called_once_with("world")
    mock.intern.assert_not_called()


def test_circle():
    mock = MockExpression(
        module="config/command_rule.py",
        intern=InternalSource("generic"),
        cmd=SubprocessSource("echo Don\\'t break the")
    )
    mock.intern.update_value(None, stat_init=True)
    mock.cmd.assert_called_once_with("circle")
    mock.intern.assert_not_called()


def test_ls():
    mock = MockExpression(
        module="config/command_rule.py",
        intern=InternalSource("generic"),
        cmd=SubprocessSource("ls -lah .")
    )
    mock.intern.update_value(None, stat_init=True)
    mock.cmd.assert_called_once_with("")
    mock.intern.assert_not_called()
