import queue
import logging
import threading
from ..Shared.Internal import Statistics

log = logging.getLogger(__name__)
log.debug("load module")

class BaseEngine():
    def __init__(self, shared=None):
        self.add_shared_object(shared)

        self._controllers = None
        self._rules = None
        self._sources = None

    def add_shared_object(self, shared):
        self.shared = shared

    def add_controller_classes(self, controllers):
        self._controllers = controllers

    def add_rule_classes(self, rules):
        self._rules = rules

    def add_source_classes(self, sources):
        self._sources = sources

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def wait(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def load(self, base_package):
        raise NotImplementedError

    @staticmethod
    def block():
        raise NotImplementedError

class BaseExpressionExecutor():
    def __init__(self, name, shared):
        self.add_name(name)
        self.add_shared(shared)
        self.init_queue()
        self.add_interrupt(None)

    def add_name(self, name):
        self.name = name

    def add_shared(self, shared):
        self.shared = shared

    def init_queue(self):
        self.incoming = self.shared.queues.get_messages_to_engine()
        self.messagetypes = self.shared.queues.MessageType
        self.queue_timeout = 0.1

    def add_interrupt(self, interrupt):
        self._interrupt = interrupt

    def has_interrupt(self):
        return self._interrupt.is_set()

    def run(self):
        raise NotImplementedError

    def loop_incoming(self):
        try:
            while not self.has_interrupt():
                if Statistics.on:
                    Statistics.set(self.name + ".incoming.queue.size", self.incoming.qsize())
                    Statistics.set(self.name + ".threading.total.count", threading.active_count())
                messagetype, incoming = self.incoming.get(block=True, timeout=self.queue_timeout)
                if messagetype == self.messagetypes.RUN_EXPRESSION:
                    source_item, expressions = incoming
                    self.handle_run_expression(source_item, expressions)
                else:
                    raise NotImplementedError

        except queue.Empty:
            pass

    def handle_run_expression(self, source_item, expressions):
        raise NotImplementedError
