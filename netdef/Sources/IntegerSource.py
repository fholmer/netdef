from . import BaseSource, Sources
from ..Interfaces.IntegerInterface import IntegerInterface

@Sources.register("IntegerSource")
class IntegerSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = IntegerInterface

