from . import DictSource, Sources
from ..Interfaces.DefaultInterface import DefaultInterface

@Sources.register("InternalSource")
class InternalSource(DictSource.DictSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface
