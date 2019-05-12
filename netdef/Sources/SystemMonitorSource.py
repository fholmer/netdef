from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.DefaultInterface import DefaultInterface

@Sources.register("SystemMonitorSource")
class SystemMonitorSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface

    def get_value_and_unit(self):
        return str(self.value)

    @property
    def value_as_string(self):
        return str(self.value)

@Sources.register("SystemMonitorByteSource")
class SystemMonitorByteSource(SystemMonitorSource):
    def get_value_and_unit(self):
        return bytes2human(self.value)

@Sources.register("SystemMonitorPercentSource")
class SystemMonitorPercentSource(SystemMonitorSource):
    def get_value_and_unit(self):
        return "{}%".format(round(self.value, 1))

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n