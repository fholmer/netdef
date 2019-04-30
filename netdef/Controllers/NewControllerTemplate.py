import logging
import datetime
from . import BaseController, Controllers
from ..Sources.BaseSource import StatusCode

# import my supported sources
from ..Sources.NewSourceTemplate import NewSourceTemplate

@Controllers.register("NewControllerTemplate")
class NewControllerTemplate(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        self.one_config_entry = self.shared.config.config(self.name, "one_config_entry", "default_value")

    def run(self):
        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene
            self.loop_outgoing() # denne kaller opp poll_*
        self.logger.info("Stopped")

    def handle_readall(self, incoming):
        raise NotImplementedError

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

    def handle_read_source(self, incoming):
        raise NotImplementedError

    def handle_write_source(self, incoming, value, source_time):
        self.logger.debug("'Write source' event to %s. value: %s at: %s", incoming.key, value, source_time)

    def poll_outgoing_item(self, item):
        if isinstance(item, NewSourceTemplate): # My
            # TODO: get new value somehow
            address = item.unpack_address()
            new_val = get_the_new_value_somehow(address)
            stime = datetime.datetime.utcnow()
            status_ok = True # Why not
            cmp_oldew = False # compare old and new value?

            if self.update_source_instance_value(item, new_val, stime, status_ok, cmp_oldew):
                self.send_outgoing(item)
