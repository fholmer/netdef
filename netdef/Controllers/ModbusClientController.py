import logging
import datetime
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ModbusIOException, ConnectionException

from . import BaseController, Controllers
from ..Sources.BaseSource import StatusCode

log = logging.getLogger(__name__)
log.debug("Loading module")

@Controllers.register("ModbusClientController")
class ModbusClientController(BaseController.BaseController):
    """
    .. caution:: Development Status :: 4 - Beta

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")

        self.oldnew = self.shared.config.config(self.name, "oldnew_comparision", 1)
        self.clear_writes_on_disconnect = self.shared.config.config(self.name, "clear_writes_on_disconnect", 1)
        self.poll_interval = self.shared.config.config(self.name, "poll_interval", 0.5)

        host = self.shared.config.config(self.name, "host", '0.0.0.0')
        port = self.shared.config.config(self.name, "port", 5020)
        self.client = ModbusClient(host, port=port)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        reconnect = False
        reconnect_timeout = 0

        self.loop_until_app_state_running()

        while not self.has_interrupt():
            self.sleep(reconnect_timeout)
            reconnect_timeout = self.shared.config.config(self.name, "reconnect_timeout", 20)

            try:
                if reconnect:
                    self.safe_disconnect()

                    if self.clear_writes_on_disconnect:
                        self.clear_incoming()

                reconnect = True
                self.logger.info("Running")

                while not self.has_interrupt():
                    self.loop_incoming(until_empty=False, until_timeout=self.poll_interval) # dispatch handle_* functions
                    self.loop_outgoing() # dispatch poll_* functions funksjonene

            except (ConnectionRefusedError, ConnectionError, ConnectionException) as error:
                self.logger.debug("Exception: %s", error)
                self.logger.error("Connection error. Reconnect in %s sec.", reconnect_timeout)
                self.safe_disconnect()

                for item in self.get_sources().values():
                    if self.update_source_instance_status(item, status_ok=False, oldnew_check=self.oldnew):
                        self.send_outgoing(item)

        self.safe_disconnect()
        self.logger.info("Stopped")

    def safe_disconnect(self):
        try:
            self.client.close()
        except Exception as error:
            self.logger.warning("Cannot disconnect client: %s", error)

    def handle_add_source(self, incoming):
        self.add_source(incoming.key, incoming)

    def handle_write_source(self, incoming, value, source_time):
        if hasattr(incoming, "unpack_unit_and_address"):
            slave_unit, register = incoming.unpack_unit_and_address()

            try:
                write_result = self.client.write_register(register, value, unit=slave_unit)
                if isinstance(write_result, ModbusIOException):
                    raise ModbusIOException

                status_ok = write_result.function_code < 0x80
                if not status_ok:
                    self.logger.error(
                        "Write error on modbus unit:%s register:%s value:%s",
                        slave_unit, register, value
                        )

            except ModbusIOException as write_error:
                self.logger.exception(write_error)
                self.logger.error(
                    "Write error on modbus unit:%s register:%s value:%s time:%s",
                    slave_unit, register, value, source_time
                    )

    def poll_outgoing_item(self, item):
        if hasattr(item, "unpack_unit_and_address"):
            slave_unit, register = item.unpack_unit_and_address()
            try:
                read_result = self.client.read_holding_registers(register, 1, unit=slave_unit)
                if isinstance(read_result, ModbusIOException):
                    raise ModbusIOException
                status_ok = read_result.function_code < 0x80
                value = read_result.registers[0]
                stime = datetime.datetime.utcnow()
                if self.update_source_instance_value(item, value, stime, status_ok, self.oldnew):
                    self.send_outgoing(item)
            except ModbusIOException as error:
                self.logger.exception(error)
