import datetime
import inspect
import os
from unittest.mock import Mock

from netdef.Engines.expression.Expression import Expression
from netdef.Rules.utils import get_module_from_string
from netdef.Shared import SharedConfig
from netdef.Shared.Shared import Shared
from netdef.Sources.BaseSource import BaseSource, StatusCode


class MockShared(Shared):
    def __init__(self, config_string=""):
        identifier = ""
        install_path = None
        proj_path = None
        read_from_files = False

        if "[general]" not in config_string:
            config_string = "[general]\nversion=1\n{}".format(config_string)

        default_config_string = config_string

        self.config = SharedConfig.Config(
            identifier, install_path, proj_path, default_config_string, read_from_files
        )
        self.sources = Mock()
        self.expressions = Mock()
        self.restart_on_exit = False


class MockSource:
    def __init__(self, expression, source):
        self.expression = expression
        self.source = source

    def update_value(
        self,
        val,
        stime=None,
        stat_none=False,
        stat_init=False,
        stat_good=False,
        stat_invalid=False,
        run_expression=True,
    ):
        "A Helper function to update values in expression"
        src = self.source
        src.get = val

        if stat_good:
            src.status_code = StatusCode.GOOD
        elif stat_init:
            src.status_code = StatusCode.INITIAL
        elif stat_invalid:
            src.status_code = StatusCode.INVALID
        elif stat_none:
            src.status_code = StatusCode.NONE
        else:
            src.status_code = StatusCode.NONE

        if isinstance(stime, datetime.datetime):
            src.source_time = stime
        else:
            src.source_time = datetime.datetime.utcnow()

        if run_expression:
            args = self.expression.get_args(self.source)
            kwargs = self.expression.get_kwargs()
            return self.expression.execute(args, kwargs)
        return None

    def assert_value(self, value):
        "A helper function to assert value and timestamp"
        assert isinstance(self.source.set_source_time, datetime.datetime)
        assert self.source.set_value == value

    def assert_called(self):
        self.source.set_callback.assert_called()

    def assert_called_once(self):
        self.source.set_callback.assert_called_once()

    def assert_called_with(self, value):
        self.source.set_callback.assert_called_with(
            self.source, value, self.source.set_source_time
        )

    def assert_called_once_with(self, value):
        self.source.set_callback.assert_called_once_with(
            self.source, value, self.source.set_source_time
        )

    def assert_any_call(self, value):
        self.source.set_callback.assert_any_call(
            self.source, value, self.source.set_source_time
        )

    def assert_not_called(self):
        self.source.set_callback.assert_not_called()

    @property
    def call_count(self):
        return self.source.set_callback.call_count

    @property
    def call_args(self):
        args, kwargs = self.source.set_callback.call_args
        src, val, stime = args
        return val

    @property
    def call_args_list(self):
        call_args_list = self.source.set_callback.call_args_list
        return [args[1] for args, kwargs in call_args_list]


class MockExpression:
    """
    Example::

        from netdef.testutils import MockExpression

        def test_hello():
            mock = MockExpression(
                module="config/command_rule.py",
                intern=InternalSource("generic"),
                cmd=CmdSource("echo hello")
            )
            mock.intern.update_value(None, stat_init=True)
            mock.cmd.assert_called_once_with("world")
            mock.intern.assert_not_called()
    """

    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._expr = None
        self._pymod = None

        for k, v in self._kwargs.items():
            if isinstance(v, Expression):
                self._expr = v
                break
            elif isinstance(v, type(os)):
                self._pymod = v
            elif isinstance(v, str) and k == "module":
                self._pymod = get_module_from_string(
                    v, __package__, os.getcwd(), "testutils", "mockexpression"
                )
            if self._pymod:
                func = self._kwargs.get("expression", "expression")
                self._expr = Expression(
                    getattr(self._pymod, func), self._pymod.__file__
                )
                break

        assert not self._expr is None

        for k, v in self._kwargs.items():
            if isinstance(v, BaseSource):
                setattr(self, k, MockSource(self._expr, v))
                v.register_set_callback(Mock())

        for arg in inspect.signature(self._expr.expression).parameters.keys():
            self._expr.add_arg(self._kwargs[arg])

    def get_module(self):
        "Returns the expression module"
        return self._pymod

    def set_init_values(self, **kwargs):
        for k, v in kwargs.items():
            attr = getattr(self, k)
            attr.update_value(val=v, stat_init=True, run_expression=False)

    def set_none_values(self, **kwargs):
        for k, v in kwargs.items():
            attr = getattr(self, k)
            attr.update_value(val=v, stat_none=True, run_expression=False)

    def get_callbacks(self):
        return ((arg, arg.set_callback) for arg in self._expr.args)

    def __getattr__(self, name):
        # this is only to please pylint
        raise AttributeError("MockExpression has no attribute '{}'".format(name))
