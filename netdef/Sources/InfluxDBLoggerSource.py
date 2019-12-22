from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.InfluxDBLoggerInterface import InfluxDBLoggerInterface, Value

@Sources.register("InfluxDBLoggerSource")
class InfluxDBLoggerSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = InfluxDBLoggerInterface
    
    def unpack_measurement(self):
        return self.key

    @staticmethod
    def make_points(interface, measurement, value, source_time, status_code):
        points = [{
            "measurement": measurement,
            "time": source_time,
            "tags": {
                "key": interface.key,
                "rule": interface.rule,
                "source": interface.source,
                "controller": interface.controller
            },
            "fields": {
                "value": value,
                "status_code": str(status_code)
            }
        }]
        return points

    def get_points(self, data, source_time, status_code):
        if isinstance(data, Value):
            return self.make_points(data, self.key, data.value, data.source_time, data.status_code)
        else:
            return self.make_points(self, self.key, data, source_time, status_code)

