import logging
import datetime
import zmq
from netdef.Controllers import BaseController, Controllers
from netdef.Sources.BaseSource import StatusCode

# import my supported sources
from ..Sources.ZmqDataAccessSource import ZmqDataAccessSource

@Controllers.register("ZmqDataAccessController")
class ZmqDataAccessController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")

        config = self.shared.config.config

        self.topic = b"" # config(self.name, "topic", "dist")
        self.publish_url = config(self.name, "publish_url", "tcp://127.0.0.1:5556")
        self.subscribe_list = config(self.name, "subscribe_urls", "{}_subscribe_urls".format(self.name))

        self.subscribe_urls = [
            url for url in self.shared.config.get_dict(self.subscribe_list).values()
        ]

        self.context = zmq.Context()
        self.pub = self.context.socket(zmq.XPUB)
        self.sub = self.context.socket(zmq.SUB)
        self.poller = zmq.Poller()

    def connect(self):
        self.pub.bind(self.publish_url)

        self.logger.info("listening to %s", self.publish_url)
        for url in self.subscribe_urls:
            self.sub.connect(url)
            self.logger.info("connecting to: %s", url)
        self.sub.setsockopt(zmq.SUBSCRIBE, self.topic)
        self.pub.setsockopt(zmq.XPUB_VERBOSE, 1)
        self.poller.register(self.pub, zmq.POLLIN)
        self.poller.register(self.sub, zmq.POLLIN)

    def loop_subscribers(self):
        try:
            events = {"first":1}
            while events and not self.has_interrupt():
                events = dict(self.poller.poll(10))

                if self.sub in events:
                    vlist = self.sub.recv_pyobj(flags=zmq.NOBLOCK)
                    for val in vlist:
                        item_key, value, stime = val
                        self.logger.debug("SUB RECV: %s %s %s", item_key, value, stime)

                        if self.has_source(item_key):
                            item = self.get_source(item_key)
                            if self.update_source_instance_value(item, value, stime, True, False):
                                self.send_outgoing(item)

                elif self.pub in events:
                    event = self.pub.recv(flags=zmq.NOBLOCK)
                    self.logger.debug("PUB RECV %s", event)
                    if event[0] == 1: # subscribe-event
                        rep = tuple((item.key, item.value, item.source_time) for item in self.get_sources().values())
                        self.pub.send_pyobj(rep)

        except zmq.ZMQError as error:
            if error.errno == 11:
                pass
            else:
                self.logger.exception(error)

    def run(self):
        self.logger.info("Running")
        self.connect()
        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene
            self.loop_subscribers() # denne kaller opp poll_*

        self.logger.info("Stopped")

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

    def handle_write_source(self, incoming, value, source_time):
        self.logger.debug("'Write source' event to %s. value: %s at: %s", incoming.key, value, source_time)
        self.pub.send_pyobj(((incoming.key, value, source_time), ), flags=zmq.NOBLOCK)
