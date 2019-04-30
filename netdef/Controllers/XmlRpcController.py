import logging
import datetime
import socket
import xmlrpc.client

from . import BaseController, Controllers
from ..Sources.BaseSource import StatusCode

# import my supported sources
from ..Sources.XmlRpcMethodCallSource import XmlRpcMethodCallSource

@Controllers.register("XmlRpcController")
class XmlRpcController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        self.send_events = self.shared.config.config(self.name, "send_events", 1)
        self.endpoint_url = self.shared.config.config(self.name, "endpoint_url", "")
        self.poll_interval = self.shared.config.config(self.name, "poll_interval", 5)
        self.timeout = self.shared.config.config(self.name, "timeout", 5)
        self.disable = self.shared.config.config(self.name, "disable", 0)

        self.endpoint = None
        if self.endpoint_url:
            socket.setdefaulttimeout(self.timeout)
            self.endpoint = xmlrpc.client.ServerProxy(self.endpoint_url)

    def run(self):
        self.logger.info("Running")
        while not self.has_interrupt():
            if self.disable:  # disble: tøm køen og loop
                self.fetch_one_incoming()
                continue
            self.loop_incoming() # denne kaller opp handle_* funksjonene
            self.sleep(self.poll_interval)
            if not self.has_interrupt():
                self.loop_outgoing() # denne kaller opp poll_*
        self.logger.info("Stopped")

    def handle_readall(self, incoming):
        raise NotImplementedError

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)
        if not self.send_events:
            incoming.status_code = StatusCode.GOOD
            incoming.get = {}

    def handle_read_source(self, incoming):
        raise NotImplementedError

    def handle_write_source(self, incoming, value, source_time):
        self.logger.info("'Write source' event to %s. value: %s", incoming.key, value)
        if self.endpoint:
            if isinstance(incoming, XmlRpcMethodCallSource):
                incoming.get = self.rpc_call(incoming, value)
                incoming.source_time = source_time
                if self.send_events:
                    if incoming.status_code == StatusCode.NONE:
                        incoming.status_code = StatusCode.INITIAL
                    else:
                        incoming.status_code = StatusCode.GOOD
                    self.send_outgoing(incoming)
                else:
                    incoming.status_code = StatusCode.GOOD
            else:
                self.logger.error("'Write source' class %s not supported", type(incoming))

    def poll_outgoing_item(self, item):
        if self.endpoint:
            if isinstance(item, XmlRpcMethodCallSource):
                request = item.poll_request()
                response = self.rpc_call(item, request)

                for sub_item in self.parse_response(response):
                    self.parse_item(sub_item)

                item.get = response
                item.source_time = datetime.datetime.utcnow()
                item.status_code = StatusCode.GOOD
                self.send_outgoing(item)

    def rpc_call(self, item, value):
        try:
            method, arguments = item.make_rpc_request(value)
            result = getattr(self.endpoint, method)(*arguments)
            return item.parse_rpc_response(result)

        except Exception as error:
            self.logger.error("%s: %s", item.get_reference(), error)
        return None

    def parse_response(self, response):
        for parser in self.get_parsers():
            if parser.can_unpack_subitems(response):
                yield from parser.unpack_subitems(response)

    def parse_item(self, item):
        for parser in self.get_parsers():
            if parser.can_unpack_value(item):
                key, source_time, value = parser.unpack_value(item)
                self.send_datachange(key, source_time, value)
    
    def send_datachange(self, key, source_time, value):
        if self.has_source(key):
            if not source_time:
                source_time = datetime.datetime.utcnow()
            source_instance = self.get_source(key)
            source_instance.get = value
            source_instance.source_time = source_time
            source_instance.status_code = StatusCode.GOOD
            self.send_outgoing(source_instance)
