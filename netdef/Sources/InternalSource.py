import pickle
from . import DictSource, Sources
from ..Interfaces.DefaultInterface import DefaultInterface

@Sources.register("InternalSource")
class InternalSource(DictSource.DictSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface

    @staticmethod
    def can_unpack_value(value):
        return True

    @staticmethod
    def unpack_value(value):
        obj = pickle.loads(value)
        return obj

    def pack_value(self, value):
        obj = pickle.dumps(value)
        return obj

