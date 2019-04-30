import logging
import time
import concurrent.futures
import opcua
from . import BaseController, Controllers
from ..Sources.BaseSource import StatusCode

log = logging.getLogger(__name__)
log.debug("Loading module")

@Controllers.register("OPCUAClientController")
class OPCUAClientController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")

        endpoint = self.shared.config.config(self.name, "endpoint", "")
        certificate = self.shared.config.config(self.name, "certificate", "")
        private_key = self.shared.config.config(self.name, "private_key", "")
        connection_timeout = self.shared.config.config(self.name, "connection_timeout", 4)
        self.oldnew = self.shared.config.config(self.name, "oldnew_comparision", 0)
        self.disable = self.shared.config.config(self.name, "disable", 0)
        self.client = opcua.Client(endpoint, connection_timeout)
        self.client.load_client_certificate(certificate)
        self.client.load_private_key(private_key)
        self.subscription = None

    def run(self):
        reconnect = False
        reconnect_timeout = 0

        keepalive_timeout = self.shared.config.config(self.name, "keepalive_timeout", 600)
        last_keepalive = time.time()

        while not self.has_interrupt():

            if self.disable:  # to disable: empty queue by calling self.fetch_one_incoming
                self.fetch_one_incoming()
                continue
            
            self.sleep(reconnect_timeout)
            reconnect_timeout = self.shared.config.config(self.name, "reconnect_timeout", 20)

            try:
                if reconnect:
                    self.safe_disconnect()
                    #TODO: sette alle verdier til StatusCode.NONE

                self.client.connect()
                
                intervall = self.shared.config.config(self.name, "subscription_interval", 100)
                handler = SubHandler(self)
                self.subscription = self.client.create_subscription(intervall, handler)

                for source_key in self.get_sources():
                    node_instance = self.client.get_node(source_key)
                    try:
                        self.subscription.subscribe_data_change(node_instance)
                    except opcua.ua.uaerrors.BadNodeIdUnknown as error:
                        self.logger.exception(error)

                reconnect = True
                last_keepalive = time.time()
                self.logger.info("Running")
                while not self.has_interrupt():
                    self.loop_incoming() # denne kaller opp handle_* funksjonene
                    time.sleep(0.01)
                    if time.time() > (last_keepalive + keepalive_timeout):
                        # self.logger.debug("Sending keepalive")
                        self.client.send_hello()
                        last_keepalive = time.time()

            except (ConnectionRefusedError, ConnectionError) as error:
                self.logger.debug(error, exc_info=True)
                self.logger.error("Connection error. Reconnect in %s sec.", reconnect_timeout)

            except (concurrent.futures.TimeoutError) as error:
                self.logger.debug(error, exc_info=True)
                self.logger.error("Timeout error. Reconnect in %s sec.", reconnect_timeout)

        self.safe_disconnect()
        self.logger.info("Stopped")

    def safe_disconnect(self):
        try:
            if self.subscription:
                self.subscription.delete()
        except Exception as error:
            self.logger.warning("Cannot delete subscription: %s", error)

        for item in self.get_sources().values():
            item.status_code = StatusCode.NONE

        try:
            self.client.disconnect()
        except Exception as error:
            self.logger.warning("Cannot disconnect client: %s", error)

    def handle_readall(self, incoming):
        raise NotImplementedError

    def handle_add_source(self, incoming):
        try:
            # key sould be of format: "ns=2;s=Channel1.Device1.Tag1"
            node_instance = self.client.get_node(incoming.key)
            self.subscription.subscribe_data_change(node_instance)
            self.add_source(incoming.key, incoming)
        except opcua.ua.uaerrors.BadNodeIdUnknown as error:
            self.logger.error("%s: %s", incoming.key, error)
        except opcua.ua.uaerrors.UaStringParsingError as error:
            self.logger.exception(error)
        #TODO: kanske lagre nodeid-instansene?

    def handle_read_source(self, incoming):
        raise NotImplementedError

    def handle_write_source(self, incoming, value, source_time):
        if self.has_source(incoming.key):
            node_instance = self.client.get_node(incoming.key)
            #print(id(node_instance), source_time)
            #TODO: kanske gjøre internt oppslag på nodeid-instansene, i stedet for å hente ny hver gang?
            node_instance.set_value(value)
        else:
            self.logger.error("Write error. Source %s not found", incoming.key)

    def loop_outgoing(self):
        for item in self.get_sources().values():
            self.poll_outgoing_item(item)

    def send_datachange(self, nodeid, value, stime, status_ok):
        if self.has_source(nodeid):
            item = self.get_source(nodeid)
            if self.update_source_instance_value(item, value, stime, status_ok, self.oldnew):
                self.send_outgoing(item)

class SubHandler(object):
    """
    Client to subscription. It will receive events from server
    """
    def __init__(self, parent):
        self.parent = parent

    def datachange_notification(self, node, value, data):
        nodeid = node.nodeid.to_string()
        item = data.monitored_item.Value
        source_value = item.Value.Value
        source_time = item.SourceTimestamp
        source_status_ok = item.StatusCode.value == 0
        #self.logger.debug("nodeid:%s, value:%s, time:%s, ok:%s", )
        self.parent.send_datachange(nodeid, source_value, source_time, source_status_ok)

    def event_notification(self, event):
        self.parent.logger.info("opcua subscription: New event: %s", event)

    def status_change_notification(self, status):
        self.parent.logger.info("opcua subscription: New status: %s", status)
