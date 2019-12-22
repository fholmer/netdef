from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.DefaultInterface import DefaultInterface

@Sources.register("InfluxDBLoggerSource")
class InfluxDBLoggerSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface
    
    def unpack_measurement(self):
        return self.key

    @staticmethod
    def make_points(item, value, source_time):
        points = [{
            "measurement": item.key,
            "time": source_time,
            "tags": {
                "key": item.key,
                "rule": item.rule,
                "source": item.source,
                "controller": item.controller
            },
            "fields": {
                "value": value,
                "status_code": str(item.status_code)
            }
        }]
        return points

    def get_points(self, value, source_time):
        return self.make_points(self, value, source_time)
