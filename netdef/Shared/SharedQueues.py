import queue
from enum import Enum
import logging

# meldingstyper
# bare ADD_SOURCE, ADD_PARSER, WRITE_SOURCE, RUN_EXPRESSION er implementert

class MessageType(Enum):
    READ_ALL = 1
    ADD_SOURCE = 2
    READ_SOURCE = 3
    WRITE_SOURCE = 4
    RUN_EXPRESSION = 5
    ADD_PARSER = 6
    REMOVE_SOURCE = 7
    TICK = 8

class SharedQueues():
    MessageType = MessageType
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self.logger = logging.getLogger(__name__)

        # dette er en dict med inncoming-køene til controllerene
        self.messages_to_controller = {}

        # inncoming-køene til regelmotorene
        self.messages_to_rule = {}

        # en liste over kontrollerene som er aktivert
        self.available_controllers = []

        # en liste over regelmotorer som er aktivert
        self.available_rules = []

        # den finnes bare én motor. dette er incoming-køen
        self.messages_to_engine = queue.Queue(maxsize)

    def add_controller(self, name):
        """ Opprett ny incoming kø til navngitt kontroller'
        """
        self.messages_to_controller[name] = queue.Queue(self.maxsize)
        self.available_controllers.append(name)

    def add_rule(self, name):
        """ Opprett ny incoming kø til navngitt regelmotor
        """
        self.messages_to_rule[name] = queue.Queue(self.maxsize)
        self.available_rules.append(name)

    def get_messages_to_controller(self, name):
        """ Returnerer køen til navngitt kontroller
        """
        return self.messages_to_controller[name]

    def get_messages_to_rule(self, name):
        """ Returnerer incoming køen til navngitt regelmotor
        """
        return self.messages_to_rule[name]

    def get_messages_to_engine(self):
        """ Returnerer motoren incoming kø
        """
        return self.messages_to_engine

    def send_message_to_controller(self, messagetype, controllername, message_object):
        try:
            self.messages_to_controller[controllername].put_nowait((messagetype, message_object))
        except KeyError:
            self.logger.error(
                "Cannot send message %s. %s not enabled.",
                message_object,
                controllername
                )

    def send_message_to_rule(self, messagetype, rule_name, message_object):
        if rule_name == "*":
            for name in self.available_rules:
                self.messages_to_rule[name].put_nowait((messagetype, message_object))
        else:
            self.messages_to_rule[rule_name].put_nowait((messagetype, message_object))

    def send_message_to_engine(self, messagetype, message_object):
        self.messages_to_engine.put_nowait((messagetype, message_object))

    def run_expressions_in_engine(self, source_instance, expressions):
        self.send_message_to_engine(
            MessageType.RUN_EXPRESSION,
            (source_instance, expressions)
        )

    def write_value_to_controller(self, source_instance, value, source_time):
        controllername = source_instance.controller
        try:
            self.messages_to_controller[controllername].put_nowait(
                (MessageType.WRITE_SOURCE, (source_instance, value, source_time))
            )
        except queue.Full:
            self.logger.error(
                "Cannot send message %s. Queue %s is full.",
                source_instance,
                controllername
            )
