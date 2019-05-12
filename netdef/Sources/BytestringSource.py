import re
import struct
from netdef.Sources import Sources, BaseSource
from ..Interfaces.BytestringInterface import ByteStringInterface

@Sources.register("BytestringSource")
class BytestringSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = ByteStringInterface

    @property
    def value_as_string(self):
        """brukes primært av webgrensesnitt til å vise verdi i tabell.
        bør overstyres for å begrense visning av store data"""
        if self.value and isinstance(self.value, bytes):
            n = len(self.value)
            return "<{}...><data len:{}>".format(self.value[:10], n)
        else:
            return super().value_as_string
