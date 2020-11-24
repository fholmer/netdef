import logging
import time
import datetime
import subprocess
import shlex
from netdef.Controllers import BaseController, Controllers
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
    """
        .. danger:: Development Status :: 3 - Alpha
    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        self.value_as_args = self.shared.config.config(self.name, "value_as_args", 1)
        self.interval_plan = None
        self.oldnew = False

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        self.logger.info("Running")

        self.loop_until_app_state_running()
        self.interval_plan = self.setup_interval_plan()

        while not self.has_interrupt():
            if self.interval_plan.has_interval():
                timeout, current_interval = self.interval_plan.next(time.time())
                self.loop_incoming(until_empty=False, until_timeout=timeout)  # dispatch handle_* functions

                for item in self.get_sources().values():
                    if item.has_poll_interval():
                        if item.get_poll_interval() == current_interval:
                            self.poll_outgoing_item(item)
            else:
                self.loop_incoming()
        self.logger.info("Stopped")

    def setup_interval_plan(self):
        interval_plan = NextInterval(time.time())

        for source in self.get_sources().values():
            if source.has_poll_interval():
                pri = source.get_poll_interval()
                if pri > 0:
                    interval_plan.add(pri)
        return interval_plan

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

    def _verify_incoming(self, incoming):
        if not self.has_source(incoming.key):
            self.logger.error(
                "%s not found",
                incoming.key
                )
            return False

        if not isinstance(incoming, SubprocessSource):
            self.logger.error(
                "Got write event for %s, but only SubprocessSource is supported",
                type(incoming)
                )
            return False
        return True


    def handle_write_source(self, incoming, value, source_time):
        self.logger.debug("'Write source' event to %s. value: %s at: %s", incoming.key, value, source_time)
        if not self._verify_incoming(incoming):
            return

        if self.value_as_args:
            cmd_as_str = incoming.get_command_and_args(value)
        else:
            cmd_as_str = incoming.get_command_and_args()
            
        new_val = stdout_from_terminal(cmd_as_str)
        stime = datetime.datetime.utcnow()
        status_ok = True

        if self.update_source_instance_value(incoming, new_val, stime, status_ok, self.oldnew):
            self.send_outgoing(incoming)

    def poll_outgoing_item(self, item):
        self.logger.debug("'Poll source' %s.", item.key)
        if not self._verify_incoming(item):
            return

        cmd_as_str = item.get_command_and_args()
        response = stdout_from_terminal(cmd_as_str)
        response = item.parse_stdout_response(response)
        stime = datetime.datetime.utcnow()
        status_ok = True

        for sub_item in self.parse_response(response):
            self.parse_item(sub_item)

        if self.update_source_instance_value(item, response, stime, status_ok, self.oldnew):
            self.send_outgoing(item)

    def parse_response(self, response):
        for parser in self.get_parsers():
            if parser.can_unpack_subitems(response):
                yield from parser.unpack_subitems(response)

    def parse_item(self, item):
        for parser in self.get_parsers():
            if parser.can_unpack_value(item):
                key, source_time, value = parser.unpack_value(item)
                self.send_datachange(key, value, source_time, True)

    def send_datachange(self, source_key, value, source_time, status_ok):
        if not self.has_source(source_key):
            return
        if not source_time:
            source_time = datetime.datetime.utcnow()
        item = self.get_source(source_key)
        if self.update_source_instance_value(
            item, value, source_time, status_ok, self.oldnew
        ):
            self.send_outgoing(item)


class NextInterval:
    "Call next() to retrieve seconds to next interval, and which interval it is"
    __slots__ = ["spans", "start"]

    def __init__(self, timestamp):
        self.spans = []
        self.start = timestamp

    def has_interval(self):
        return True if self.spans else False

    def add(self, interval):
        new_span = [self.start + interval, interval]
        if not new_span in self.spans:
            self.spans.append(new_span)

    def next(self, now):
        okay_then = min(self.spans)
        when, what = okay_then
        if when < now:
            when = now
        okay_then[0] = when + what
        return when - now, what
