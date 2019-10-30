import logging
import datetime
import os
import hashlib
from . import BaseController, Controllers
from ..Sources.BaseSource import StatusCode

@Controllers.register("InternalController")
class InternalController(BaseController.BaseController):
    """
    .. tip:: Development Status :: 5 - Production/Stable

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        self.send_events = self.shared.config.config(self.name, "send_events", 0)
        self.send_init_event = self.shared.config.config(self.name, "send_init_event", 0)
        self.persistent_value = self.shared.config.config(self.name, "persistent_value", 0)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # dispatch handle_* functions
            self.loop_outgoing() # dispatch poll_* functions
        
        if self.persistent_value:
            self.logger.info("Write cache to disk ...")
            self.store_to_disk()
        self.logger.info("Stopped")

    @staticmethod
    def get_cache_filename(key):
        return hashlib.sha256(key.encode("utf8", errors="ignore")).hexdigest()

    def store_to_disk(self):
        cache_dir = os.path.join("db", "internal")
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)
        for source in self.get_sources().values():
            if source.can_unpack_value(""):
                data = source.pack_value(source.value)
                cache = os.path.join(cache_dir, self.get_cache_filename(source.key))
                with open(cache, "wb") as f:
                    f.write(data)

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

        init_value = {}
        if self.persistent_value:
            cache = os.path.join("db", "internal",  self.get_cache_filename(incoming.key))
            if os.path.isfile(cache) and incoming.can_unpack_value(""):
                with open(cache, "rb") as f:
                    data = f.read()
                    init_value = incoming.unpack_value(data)
        
        if not self.send_events:
            incoming.status_code = StatusCode.INITIAL
            incoming.get = init_value
            incoming.source_time = datetime.datetime.utcnow()
        if self.send_init_event:
            incoming.status_code = StatusCode.INITIAL
            incoming.get = init_value
            incoming.source_time = datetime.datetime.utcnow()
            self.send_outgoing(incoming)


    def handle_write_source(self, incoming, value, source_time):
        # vi gjør ikke så mye annet enn å tidsstemple nye verdier
        # og sette statuskoden
        
        incoming.get = value
        incoming.source_time = source_time

        prev_st = incoming.status_code

        if prev_st == StatusCode.NONE:
            incoming.status_code = StatusCode.INITIAL
        else:
            incoming.status_code = StatusCode.GOOD

        if self.send_events:
            self.send_outgoing(incoming)

    def poll_outgoing_item(self, item):
        pass
