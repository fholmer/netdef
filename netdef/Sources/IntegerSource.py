from ..Interfaces.IntegerInterface import IntegerInterface
from . import BaseSource, Sources


@Sources.register("IntegerSource")
class IntegerSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = IntegerInterface
