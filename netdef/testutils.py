import datetime
import inspect
import os
from unittest.mock import Mock

from netdef.Engines.expression.Expression import Expression
from netdef.Rules.utils import get_module_from_string
from netdef.Sources.BaseSource import BaseSource, StatusCode


class MockSource():
    def __init__(self, expression, source):
        self.expression = expression
        self.source = source

    def update_value(self, val, stime=None, stat_none=False, stat_init=False, stat_good=False, stat_invalid=False, run_expression=True):
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
        self.source.set_callback.assert_called_with(self.source, value, self.source.set_source_time)

    def assert_called_once_with(self, value):
        self.source.set_callback.assert_called_once_with(self.source, value, self.source.set_source_time)

    def assert_any_call(self, value):
        self.source.set_callback.assert_any_call(self.source, value, self.source.set_source_time)

    def assert_not_called(self):
        self.source.set_callback.assert_not_called()


class MockExpression():
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._expr = None

        for k, v in self._kwargs.items():
            if isinstance(v, Expression):
                self._expr = v
                break
            elif isinstance(v, str) and k == "module":
                _pymod = get_module_from_string(v, __package__, os.getcwd(), "testutils", "mockexpression")
                func = self._kwargs.get("expression", "expression")
                self._expr = Expression(getattr(_pymod, func), _pymod.__file__)

        assert not self._expr is None

        for k, v in self._kwargs.items():
            if isinstance(v, BaseSource):
                setattr(self, k, MockSource(self._expr, v))
                v.register_set_callback(Mock())

        for arg in inspect.signature(self._expr.expression).parameters.keys():
            self._expr.add_arg(self._kwargs[arg])
