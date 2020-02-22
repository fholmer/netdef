import datetime
import json
import logging

from netdef.Interfaces.DefaultInterface import DefaultInterface
from netdef.Interfaces.datamessage import DataDefinition, DataMessage
from netdef.Sources import BaseSource, Sources

log = logging.getLogger(__name__)

log.debug("Loading module")


@Sources.register("MQTTDataMessageSource")
class MQTTDataMessageSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.debug("init %s", self.key)

        self.interface = DefaultInterface

    @staticmethod
    def make_message(topic, datamessage):
        """
        Wraps given datamessage into a json-payload

        :param str topic: mqtt topic
        :param DataMessage datamessage: a datamessage object
        :return: tuple of topic and json payload
        :rtype: tuple
        """
        payload = datamessage.to_json()
        return topic, payload

    @staticmethod
    def parse_message(topic, payload):
        """
        Parse given json-payload into a datamessage object

        :param str topic: mqtt topic
        :param str payload: json payload
        :return: a :class:`DataMessage` object
        :rtype: DataMessage
        """
        if isinstance(payload, bytes):
            payload = str(payload, "utf8")
        datamessage = DataMessage.from_json(payload)
        return topic, datamessage

    def pack_value(self, value, stime, status_code, origin):
        "pack the value and stime into a mqtt payload"
        payload = DataMessage(
            key=self.key,
            value=value,
            source_time=stime.timestamp(),
            status_code=status_code,
            origin=origin,
            extension={}
        )
        return payload

    @staticmethod
    def can_unpack_value(value):
        "Check if it is possible to extract a value from the payload"
        if isinstance(value, DataMessage):
            return True
        return False

    @staticmethod
    def unpack_value(value):
        """
        Return a tuple with key, time and value from the mqtt payload
        :param DataMessage value: datamessage from mqtt payload
        :returns: tuple(key, source_time, value, origin)
        :rtype: tuple
        """
        source_time = datetime.datetime.utcfromtimestamp(value.source_time)
        return value.key, source_time, value.value, value.status_code, value.origin
