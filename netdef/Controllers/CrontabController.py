import logging
import time
import datetime
import crontab
from netdef.Controllers import BaseController, Controllers
from netdef.Sources.BaseSource import StatusCode

log = logging.getLogger(__name__)
log.debug("Loading module")

@Controllers.register("CrontabController")
class CrontabController(BaseController.BaseController):
    """
    .. tip:: Development Status :: 5 - Production/Stable

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        log.info("init")
        self.send_inital_value = self.shared.config.config(self.name, "send_inital_value", 0)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        log.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # dispatch handle_* functions
            self.loop_outgoing() # dispatch poll_* functions
            time.sleep(0.1)
        log.info("Stopped")

    def handle_add_source(self, incoming):
        self.add_source(incoming.key, incoming)

    def handle_write_source(self, incoming, value):
        pass #log.debug("Write source event %s %s", incoming.key, value)

    def poll_outgoing_item(self, item):
        """
        Check if it is time to trigger event for given source

        :param item: source instance to check
        
        """
        if item.source == "CrontabSource":
            now = datetime.datetime.utcnow()
            future = crontab.CronTab(item.key).next(default_utc=True, delta=False)
            future = datetime.datetime.utcfromtimestamp(future)

            prev_val = item.get
            prev_st = item.status_code

            if prev_st == StatusCode.NONE:
                item.status_code = StatusCode.INITIAL
                item.get = future
                item.source_time = now
                if self.send_inital_value:
                    log.debug("Initial %s %s", item.key, future)
                    self.send_outgoing(item)
            else:
                if now >= prev_val:
                    log.debug("next %s at %s now: %s", item.key, future, now)
                    item.status_code = StatusCode.GOOD
                    item.get = future
                    item.source_time = now
                    self.send_outgoing(item)
