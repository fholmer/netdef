import datetime
import hashlib
import logging
import os
import re
import time

from ..Sources.BaseSource import StatusCode
from . import BaseController, Controllers


@Controllers.register("InternalController")
class InternalController(BaseController.BaseController):
    """
    .. tip:: Development Status :: 5 - Production/Stable

    Internal variables that works just like any other value from a controller.
    Can trigger events on valuechanges. State can be cached to disk.

    :param str name: The name is used i logfile and default.ini
    :param Shared shared: Instance of applications shared object.


    **Configuration**

    .. code-block:: ini

        [InternalController]
        send_init_event = 0
        send_events = 0
        persistent_value = 0
        key_in_filename = 0

    Options
        * **send_init_event** -- trigger RUN_EXPRESSION with StatusCode.INITIAL
          for every source at startup
        * **send_events** -- trigger a RUN_EXPRESSION message for every
          WRITE_SOURCE message
        * **persistent_value** -- store values to disk
        * **key_in_filename** -- use source key as prefix in filename for
          persistent storage
        
    **Sequence diagram**

    .. seqdiag::

        seqdiag app{
            activation = none;
            default_note_color = LemonChiffon;
            span_height = 12;
            edge_length = 200;

            Queue [color=LemonChiffon];
            Controller [label=InternalController,color=LemonChiffon];

            === Initialization ===
            Queue -> Controller [label="APP_STATE, SETUP"]
            === Setup ===
            Queue -> Controller [label="ADD_SOURCE, source [n]"]
            Queue -> Controller [label="APP_STATE, RUNNING"]
            === Running ===
            === Begin loop ===
            Queue -> Controller [
                label="
                    WRITE_SOURCE,
                    source [n], value, timestamp",
                note="
                    Update value of
                    source [n]"
            ]
            ... ...
            Controller -> Queue [
                label="RUN_EXPRESSION, source [n]",
                note="
                    Value change
                    in source [n]"
            ]
            === End Loop ===
        }


    """

    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        config = self.shared.config.config

        self.send_events = config(self.name, "send_events", 0)
        self.send_init_event = config(self.name, "send_init_event", 0)
        self.persistent_value = config(self.name, "persistent_value", 0)
        self.key_in_filename = config(self.name, "key_in_filename", 0)

        # cyclic storage
        self.next_write_delta = 60
        self.next_write = time.time() + self.next_write_delta
        self.utcnow = datetime.datetime.utcnow()

        # filename prefix
        self.prefix = re.compile(r"[^\w \-\.]")

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        self.logger.info("Running")
        while not self.has_interrupt():
            # dispatch handle_* functions
            self.loop_incoming()
            if time.time() > self.next_write:
                self.next_write = time.time() + self.next_write_delta

                # dispatch poll_* functions
                self.loop_outgoing()

                self.utcnow = datetime.datetime.utcnow()

        if self.persistent_value:
            self.logger.info("Write cache to disk ...")
            self.store_to_disk()
        self.logger.info("Stopped")

    def get_cache_filename(self, key):
        """
        Generate sha256 hash to be used as filename.
        If config key_in_filename=1 then key will be prefixed to the
        hexdigest. Valid characters: a-z A-Z 0-9 _.-

        :param str key: string to encode
        :return: filename
        """
        if self.key_in_filename:
            prefix = self.prefix.sub("_", key) + "."
        else:
            prefix = ""

        return (
            prefix
            + hashlib.sha256(key.encode("utf8", errors="ignore")).hexdigest()
            + ".db"
        )

    def store_to_disk(self, item=None):
        """
        Store sources into files at [proj-path]/db/internal/
        """
        cache_dir = os.path.join("db", "internal")
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)
        for source in self.get_sources().values():
            if item is None or (item is source):
                if source.can_unpack_value(""):
                    data = source.pack_value(source.value)
                    cache = os.path.join(cache_dir, self.get_cache_filename(source.key))
                    self.logger.debug("write %s", cache)
                    with open(cache, "wb") as f:
                        f.write(data)

    def handle_add_source(self, incoming):
        """
        Add given source instance to internal source list

        :param InternalSource incoming: source instance
        """
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

        init_value = {}
        if self.persistent_value:
            cache = os.path.join(
                "db", "internal", self.get_cache_filename(incoming.key)
            )
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
        """
        Update internal dict with new value.

        :param InternalSource incoming: source instance
        :param value: frozen value of instance
        :param datetime.datetime source_time: value timestamp
        """

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
        """
        Check if given source should be cached to disk.

        :param InternalSource item: source instance
        """
        if self.persistent_value and item.source_time:
            if item.source_time >= self.utcnow:
                self.store_to_disk(item)
