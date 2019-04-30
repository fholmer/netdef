from . import BaseSource, Sources
from ..Interfaces.DefaultInterface import DefaultInterface

@Sources.register("DictSource")
class DictSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface
