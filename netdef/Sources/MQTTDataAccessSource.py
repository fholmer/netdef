import logging
import json
import datetime
from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.DefaultInterface import DefaultInterface

log = logging.getLogger(__name__)

log.debug("Loading module")

@Sources.register("MQTTDataAccessSource")
class MQTTDataAccessSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.debug("init %s", self.key)

        self.interface = DefaultInterface
    
    @staticmethod
    def make_message(topic, payload):
        payload = json.dumps(payload)
        return topic, payload

    @staticmethod
    def parse_message(topic, payload):
        if isinstance(payload, bytes):
            payload = str(payload, "utf8")
        payload = json.loads(payload)
        return topic, payload

    def pack_value(self, value, stime):
        payload = {
                "value":value,
                "source_time":stime.timestamp(),
                "key":self.key
        }
        return payload

    @staticmethod
    def can_unpack_value(value):
        if isinstance(value, dict) and "key" in value:
            return True
        return False

    @staticmethod
    def unpack_value(value):
        source_time = datetime.datetime.utcfromtimestamp(value["source_time"])
        return value["key"], source_time, value["value"]
