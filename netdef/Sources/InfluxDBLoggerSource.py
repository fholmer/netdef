from netdef.Interfaces.InfluxDBLoggerInterface import InfluxDBLoggerInterface, Value
from netdef.Sources import BaseSource, Sources


@Sources.register("InfluxDBLoggerSource")
class InfluxDBLoggerSource(BaseSource.BaseSource):
    """
    A dataholder class to be used with :class:`InfluxDBLoggerController`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = InfluxDBLoggerInterface

    def unpack_measurement(self):
        """
        Returns self.key. Override to change measurement name.
        """
        return self.key

    @staticmethod
    def make_points(interface, measurement, value, source_time, status_code):
        """
        Make a list suitable as argument for :func:`InfluxDBClient.write_points`

        :param interface: an object with key, rule, source an controller attrs
        :type interface: BaseSource, InfluxDBLoggerInterface
        :param str measurement: influxdb measurement name
        :param value: measurement field.value
        :param datetime.datetime source_time: measurement time
        :param BaseSource.StatusCode status_code: measurement field.status_code

        :returns: a list of dicts
        """
        points = [
            {
                "measurement": measurement,
                "time": source_time,
                "tags": {
                    "key": interface.key,
                    "rule": interface.rule,
                    "source": interface.source,
                    "controller": interface.controller,
                },
                "fields": {"value": value, "status_code": str(status_code)},
            }
        ]
        return points

    def get_points(self, data, source_time, status_code):
        """
        Returns a list suitable as argument for :func:`InfluxDBClient.write_points`

        :param InfluxDBLoggerInterface.Value data: an object with data to store in influxdb
        :param datetime.datetime source_time: measurement time
        :param BaseSource.StatusCode status_code: measurement field.status_code

        :returns: a list of dicts
        """

        if isinstance(data, Value):
            return self.make_points(
                data, self.key, data.value, data.source_time, data.status_code
            )
        else:
            return self.make_points(self, self.key, data, source_time, status_code)
