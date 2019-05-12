import logging
import time
import datetime
import urllib.request
import urllib.parse
import urllib.error
import http.client
import json
#import base64

from netdef.Controllers import BaseController, Controllers
from netdef.Sources.BaseSource import StatusCode

log = logging.getLogger(__name__)
log.debug("Loading module")

@Controllers.register("RESTJsonController")
class RESTJsonController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(name)
        self.logger.info("init")
        self.encoding = self.shared.config.config(self.name, "encoding", "utf-8")
        self.poll_url = self.shared.config.config(self.name, "poll_url", "")
        self.post_url = self.shared.config.config(self.name, "post_url", "")
        self.get_url = self.shared.config.config(self.name, "get_url", "")
        self.poll_interval = self.shared.config.config(self.name, "poll_interval", 1.0)
        self.connect_url = self.shared.config.config(self.name, "connect_url", "")
        self.retry = self.shared.config.config(self.name, "retry", 3)
        self.reconnect_timeout = self.shared.config.config(self.name, "reconnect_timeout", 20)
        self.urlerrors = 0
        self.urlopen = urllib.request.urlopen
        #self.auth_header = None

        self.disable = self.shared.config.config(self.name, "disable", 0)

        authorization = self.shared.config.config(self.name, "authorization", "")

        if authorization == 'basic':
            username = self.shared.config.config(self.name, "username", "")
            password = self.shared.config.config(self.name, "password", "")

            auth_handler = urllib.request.HTTPBasicAuthHandler()
            auth_handler.add_password(
                realm=None,
                uri=[self.poll_url, self.connect_url, self.post_url],
                user=username,
                passwd=password)
            self.urlopen = urllib.request.build_opener(auth_handler).open
            #credentials = ('%s:%s' % (username, password))
            #encoded_credentials = base64.b64encode(credentials.encode('ascii'))
            #self.auth_header = ('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))

    def run(self):
        
        self.logger.info("Running")
        self.connect()
        while not self.has_interrupt():

            if self.disable:  # to disable: empty queue by calling self.fetch_one_incoming
                self.fetch_one_incoming()
            else:
                self.loop_incoming() # denne kaller opp handle_* funksjonene
                self.loop_outgoing() # denne kaller opp poll_*
            time.sleep(0.1)
        self.logger.info("Stopped")

    def handle_readall(self, incoming):
        raise NotImplementedError

    def handle_add_source(self, incoming):
        add_source_message = incoming.pack_add_source()
        if add_source_message:
            self._write(add_source_message)

        self.add_source(incoming.key, incoming)

    def handle_read_source(self, incoming):
        raise NotImplementedError

    def handle_write_source(self, incoming, value):
        data = incoming.pack_value(value)
        if data:
            self._write(data)

    def connect(self):
        data = self._connect()
        #TODO: behandle motatt data med StatusCode.INITIAL

    def loop_outgoing(self):
        time.sleep(self.poll_interval)
        data = self._poll()
        if isinstance(data, dict):
            for tupleitem in data.values():
                self.parse_item(tupleitem)
        elif isinstance(data, list):
            for item in data:
                self.parse_item(item)
        elif data:
            self.parse_item(data)

    def parse_item(self, item):
        #self.logger.debug(item)
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

    def urlerrorhandling(self):
        self.urlerrors += 1
        if self.urlerrors >= self.retry:
            self.urlerrors = 0
            self.logger.error("Timeout error. Reconnect in %s sec.", self.reconnect_timeout)
            time.sleep(self.reconnect_timeout)

    def _write(self, dict_data):
        #data = urllib.parse.urlencode(dict_data)
        data = json.dumps(dict_data)
        data = data.encode('ascii')
        headers = {'Content-Type': 'application/json'}
        url = self.post_url
        request = urllib.request.Request(url, data=data, headers=headers)
        try:
            with self.urlopen(request) as f:
                self.logger.debug(f.read().decode('utf-8'))
        except (
                http.client.RemoteDisconnected,
                urllib.error.URLError
                ) as rem_err:
            self.logger.error("%s", rem_err)

    def _read(self, key):
        data = None
        try:
            with self.urlopen(self.get_url.format(key)) as f:
                data = f.read().decode('utf-8')
                data = json.loads(data)

        except (
                http.client.RemoteDisconnected,
                urllib.error.URLError
                ) as rem_err:
            self.logger.error("%s: %s", key, rem_err)
            self.urlerrorhandling()
        finally:
            return data

    def _poll(self):
        data = None
        try:
            with self.urlopen(self.poll_url) as f:
                data = f.read().decode('utf-8')
                data = json.loads(data)
        except (
                http.client.RemoteDisconnected,
                urllib.error.URLError
                ) as rem_err:
            self.logger.error("%s", rem_err)
            self.urlerrorhandling()
        finally:
            return data

    def _connect(self):
        data = None
        try:
            with self.urlopen(self.connect_url) as f:
                data = f.read().decode('utf-8')
                data = json.loads(data)
        except (
                http.client.RemoteDisconnected,
                urllib.error.URLError
                ) as rem_err:
            self.logger.error("%s", rem_err)
            self.urlerrorhandling()
        finally:
            return data
