from .DefaultInterface import DefaultInterface
from collections import namedtuple

Value = namedtuple("Value", ["key", "source", "rule", "controller", "value", "source_time", "status_code"])

class InfluxDBLoggerInterface(DefaultInterface):

    def __init__(self, value):
        if isinstance(value, Value):
            super().__init__(value)
        else:
            super().__init__(Value(value))
    
    @classmethod
    def make(cls, key, source, rule, controller, value, source_time, status_code):
        return cls(Value(
            key=key,
            source=source,
            rule=rule,
            controller=controller,
            value=value,
            source_time=source_time,
            status_code=status_code
        ))
