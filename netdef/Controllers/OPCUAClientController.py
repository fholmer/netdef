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
    """
    .. caution:: Development Status :: 4 - Beta

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")

        self.shared.config.set_hidden_value(self.name, "user")
        self.shared.config.set_hidden_value(self.name, "password")

        self.oldnew = self.config("oldnew_comparision", 0)
        self.disable = self.config("disable", 0)

        endpoint = self.config("endpoint", "")
        certificate = self.config("certificate", "")
        private_key = self.config("private_key", "")
        connection_timeout = self.config("connection_timeout", 4)
        username = self.config("user", "")
        password = self.config("password", "")

        name = self.config("name", "Pure Python Client")
        description = self.config("description", name)
        application_uri = self.config("application_uri", "urn:freeopcua:client")
        product_uri = self.config("product_uri", "urn:freeopcua.github.io:client")

        secure_channel_timeout = self.config("secure_channel_timeout", 3600000)  # 1 hour
        session_timeout = self.config("session_timeout", 3600000)  # 1 hour

        self.security_string = "" # format: Policy,Mode,certificate,private_key

        if self.config("basic128rsa15_sign_on", 0):
            self.security_string = "Basic128Rsa15,Sign,{},{}".format(certificate, private_key)

        elif self.config("basic128rsa15_signandencrypt_on", 0):
            self.security_string = "Basic128Rsa15,SignAndEncrypt,{},{}".format(certificate, private_key)

        elif self.config("basic256_sign_on", 0):
            self.security_string = "Basic256,Sign,{},{}".format(certificate, private_key)

        elif self.config("basic256_signandencrypt_on", 0):
            self.security_string = "Basic256,SignAndEncrypt,{},{}".format(certificate, private_key)

        elif self.config("basic256sha256_sign_on", 0):
            self.security_string = "Basic256Sha256,Sign,{},{}".format(certificate, private_key)

        elif self.config("basic256sha256_signandencrypt_on", 0):
            self.security_string = "Basic256Sha256,SignAndEncrypt,{},{}".format(certificate, private_key)

        elif self.config("nosecurity_on", 1):
            self.security_string = ""

        self.client = opcua.Client(endpoint, connection_timeout)

        self.client.description = description
        self.client.name = name
        self.client.application_uri = application_uri
        self.client.product_uri = product_uri

        self.client.secure_channel_timeout = secure_channel_timeout
        self.client.session_timeout = session_timeout


        if username:
            self.client.set_user(username)
            self.client.set_password(password)

        # use this to use x509 cert identification instead of username/password or anonymous
        certificate_on = self.config("certificate_basic256sha256_on", 0)
        if certificate_on:
            self.client.load_client_certificate(certificate)
            self.client.load_private_key(private_key)

        self.subscription = None

    def config(self, key, default):
        return self.shared.config.config(self.name, key, default)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"

        self.sleep(1)
        reconnect = False
        reconnect_timeout = 0

        keepalive_timeout = self.config("keepalive_timeout", 600)
        last_keepalive = time.time()

        while not self.has_interrupt():

            if self.disable:  # to disable: empty queue by calling self.fetch_one_incoming
                self.fetch_one_incoming()
                continue
            
            self.sleep(reconnect_timeout)
            reconnect_timeout = self.config("reconnect_timeout", 20)

            try:
                if reconnect:
                    self.safe_disconnect()
                    #TODO: sette alle verdier til StatusCode.NONE

                if self.security_string:
                    self.client.set_security_string(self.security_string)

                self.client.connect()
                
                intervall = self.config("subscription_interval", 100)
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
                    self.loop_incoming() # dispatch handle_* functions

                    if time.time() > (last_keepalive + keepalive_timeout):
                        # self.logger.debug("Sending keepalive")
                        self.client.send_hello()
                        last_keepalive = time.time()

            except (ConnectionRefusedError, ConnectionError) as error:
                self.logger.debug(error, exc_info=True)
                self.logger.error("Connection error. Reconnect in %s sec.", reconnect_timeout)

            except (concurrent.futures.TimeoutError, OSError) as error:
                self.logger.debug(error, exc_info=True)
                self.logger.error("Timeout error. Reconnect in %s sec.", reconnect_timeout)
            
            except opcua.ua.uaerrors.UaStatusCodeError as error:
                self.logger.debug(error, exc_info=True)
                self.logger.error("UaStatusCodeError: %s. Reconnect in %s sec.", error, reconnect_timeout)

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

    def handle_add_source(self, incoming):
        try:
            # key should be of format: "ns=2;s=Channel1.Device1.Tag1"
            node_instance = self.client.get_node(incoming.key)
            self.subscription.subscribe_data_change(node_instance)
            self.add_source(incoming.key, incoming)
        except opcua.ua.uaerrors.BadNodeIdUnknown as error:
            self.logger.error("%s: %s", incoming.key, error)
        except opcua.ua.uaerrors.UaStringParsingError as error:
            self.logger.exception(error)
        #TODO: kanske lagre nodeid-instansene?

    def handle_write_source(self, incoming, value, source_time):
        if self.has_source(incoming.key):
            node_instance = self.client.get_node(incoming.key)
            #print(id(node_instance), source_time)
            #TODO: kanske gjøre internt oppslag på nodeid-instansene, i stedet for å hente ny hver gang?
            #TODO: hente datatype med v.get_data_type_as_variant_type()
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
