from netdef.Sources import BaseSource, Sources
from netdef.Interfaces import UnitOfValueInterface

bytes2human = UnitOfValueInterface.bytes2human

@Sources.register("SystemMonitorSource")
class SystemMonitorSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = self.get_interface()

    @staticmethod
    def get_interface():
        return UnitOfValueInterface.NoUnitInterface

    def get_value_and_unit(self):
        return self.interface(self.value).get_value_and_unit()

    @property
    def value_as_string(self):
        ""
        return str(self.value)

@Sources.register("SystemMonitorByteSource")
class SystemMonitorByteSource(SystemMonitorSource):
    @staticmethod
    def get_interface():
        return UnitOfValueInterface.ByteUnitInterface

@Sources.register("SystemMonitorPercentSource")
class SystemMonitorPercentSource(SystemMonitorSource):
    @staticmethod
    def get_interface():
        return UnitOfValueInterface.PercentUnitInterface
