import datetime
import logging

from requests.exceptions import RequestException

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from netdef.Controllers import BaseController, Controllers
from netdef.Sources.BaseSource import StatusCode

# import my supported sources
from netdef.Sources.InfluxDBLoggerSource import InfluxDBLoggerSource


@Controllers.register("InfluxDBLoggerController")
class InfluxDBLoggerController(BaseController.BaseController):
    """
    .. danger:: Development Status :: 3 - Alpha

    A logging controller. Its purpose is to store every
    write event into influxdb.

    """

    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        self.dsn = self.shared.config.config(
            self.name, "dsn", "influxdb:///netdef_generic_db"
        )
        self.client = InfluxDBClient.from_dsn(self.dsn)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        reconnect_timeout = 0

        while not self.has_interrupt():
            self.sleep(reconnect_timeout)
            reconnect_timeout = self.shared.config.config(
                self.name, "reconnect_timeout", 20
            )

            try:
                self.logger.info("Running")
                self.client.create_database(self.client._database)
                while not self.has_interrupt():
                    self.loop_incoming()  # dispatch handle_* functions
                    # self.loop_outgoing() # dispatch poll_* functions

            except (
                InfluxDBClientError,
                InfluxDBServerError,
                RequestException,
            ) as error:
                self.logger.debug("Exception: %s", error)
                self.logger.error(
                    "Connection error. Reconnect in %s sec.", reconnect_timeout
                )
                self.statistics_update()

        self.logger.info("Stopped")

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        if isinstance(incoming, InfluxDBLoggerSource):
            self.add_source(incoming.unpack_measurement(), incoming)

    def handle_write_source(self, incoming, value, source_time):
        """
        Write given value and timestamp into influxdb

        :param InfluxDBLoggerSource incoming: source instance
        :param value: frozen value if instance
        :param datetime.datetime source_time: value timestamp
        """
        if isinstance(incoming, InfluxDBLoggerSource):
            points = incoming.get_points(value, source_time, incoming.status_code)
        else:
            points = InfluxDBLoggerSource.make_points(
                incoming, incoming.key, value, source_time, incoming.status_code
            )

        try:
            if not self.client.write_points(points):
                self.logger.error(
                    "Write error on influxdb db:%s measurement:%s value:%s time:%s",
                    self.client._database,
                    incoming.key,
                    value,
                    source_time,
                )
        except (InfluxDBServerError, RequestException) as write_error:
            self.logger.exception(write_error)
            self.logger.error(
                "Server error on influxdb db:%s measurement:%s value:%s time:%s",
                self.client._database,
                incoming.key,
                value,
                source_time,
            )

        self.logger.debug(
            "'Write source' event to %s. value: %s at: %s",
            incoming.key,
            value,
            source_time,
        )
