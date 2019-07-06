import logging
import datetime
import subprocess
import shlex
from netdef.Controllers import BaseController, Controllers
from netdef.Sources.BaseSource import StatusCode

from ..Sources.SubprocessSource import SubprocessSource

def stdout_from_terminal(command_as_str, err_msg=None):
    command_args = shlex.split(command_as_str)
    try:
        res = subprocess.run(command_args, stdout=subprocess.PIPE).stdout
        return str(res, errors="replace")
    except Exception as error:
        if err_msg is None:
            return str(error)
        else:
            return err_msg

@Controllers.register("SubprocessController")
class SubprocessController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        self.value_as_args = self.shared.config.config(self.name, "value_as_args", 1)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene
        self.logger.info("Stopped")

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

    def handle_write_source(self, incoming, value, source_time):
        self.logger.debug("'Write source' event to %s. value: %s at: %s", incoming.key, value, source_time)
        if not self.has_source(incoming.key):
            self.logger.error(
                "%s not found",
                incoming.key
                )
            return

        if not isinstance(incoming, SubprocessSource):
            self.logger.error(
                "Got write event for %s, but only SubprocessSource is supported",
                type(incoming)
                )
            return

        if self.value_as_args:
            cmd_as_str = incoming.get_command_and_args(value)
        else:
            cmd_as_str = incoming.get_command_and_args()
            
        new_val = stdout_from_terminal(cmd_as_str)
        stime = datetime.datetime.utcnow()
        status_ok = True # Why not
        cmp_oldew = False # compare old and new value?

        if self.update_source_instance_value(incoming, new_val, stime, status_ok, cmp_oldew):
            self.send_outgoing(incoming)
