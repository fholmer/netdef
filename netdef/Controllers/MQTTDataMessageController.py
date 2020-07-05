import logging
import uuid

import paho.mqtt.client as mqtt
from netdef.Controllers import BaseController, Controllers
from netdef.Sources.BaseSource import StatusCode

# import my supported sources
from ..Sources.MQTTDataMessageSource import MQTTDataMessageSource


@Controllers.register("MQTTDataMessageController")
class MQTTDataMessageController(BaseController.BaseController):

    """
    .. danger:: Development Status :: 3 - Alpha

    """

    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")

        config = self.shared.config.config

        self.topic_prefix = config(self.name, "topic_prefix", "NetdefDataMessage/")
        self.host = config(self.name, "host", "127.0.0.1")
        self.port = config(self.name, "port", 1883)
        self.keepalive = config(self.name, "keepalive", 60)
        self.origin = uuid.uuid1().urn
        self.origin = config(self.name, "origin", self.origin)
        self.ignore_origin = config(self.name, "ignore_messages_from_origin", 1)

        self.publish_qos = config(self.name, "publish_qos", 0)
        self.publish_retain = bool(config(self.name, "publish_retain", 1))

        self.subscribe_list = config(
            self.name, "subscribe_topics", "{}_subscribe_topics".format(self.name)
        )

        self.subscribe_topics = [
            topic for topic in self.shared.config.get_dict(self.subscribe_list).values()
        ]

        self.subscribe_to_prefix = config(
            self.name, "subscribe_to_prefix", self.ignore_origin
        )
        if self.subscribe_to_prefix:
            self.subscribe_topics.append("#")

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def get_topic(self, topic):
        return "{}{}".format(self.topic_prefix, topic)

    def get_key(self, topic):
        if topic.find(self.topic_prefix) == 0:
            return topic[len(self.topic_prefix) :]
        return topic

    def mqtt_connect(self):
        self.client.connect(self.host, self.port, self.keepalive)

    def mqtt_safe_disconnect(self):
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.debug("Connected with result code %s", rc)
        for topic in self.subscribe_topics:
            client.subscribe(self.get_topic(topic))
            self.logger.info("subscribe to %s", self.get_topic(topic))

    def on_disconnect(self, client, userdata, rc):
        self.logger.debug("Disconnected with result code %s", rc)

    def on_message(self, client, userdata, msg):
        self.logger.debug("%s %s ", msg.topic, msg.payload)
        item_key = self.get_key(msg.topic)
        if self.has_source(item_key):
            item = self.get_source(item_key)
            try:
                item_key, data = item.parse_message(item_key, msg.payload)
                if item.can_unpack_value(data):
                    key, stime, value, status_code, origin = item.unpack_value(data)
                    assert item_key == key
                    status_ok = isinstance(status_code, int) and status_code > 0
                    if self.update_source_instance_value(
                        item, value, stime, status_ok, False
                    ):
                        if not self.ignore_origin or (origin != self.origin):
                            self.send_outgoing(item)
            except Exception as error:
                self.logger.error("could not parse payload of topic %s", msg.topic)

    def loop_mqtt(self):
        rc = self.client.loop(timeout=1.0)
        # if rc != mqtt.MQTT_ERR_SUCCESS:
        if rc == mqtt.MQTT_ERR_CONN_LOST:
            raise OSError(mqtt.error_string(rc))

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        self.logger.info("Running")
        can_reconnect = False
        reconnect_timeout = 0

        while not self.has_interrupt():
            self.sleep(reconnect_timeout)
            reconnect_timeout = self.shared.config.config(
                self.name, "reconnect_timeout", 20
            )
            try:
                if can_reconnect:
                    self.mqtt_safe_disconnect()

                self.mqtt_connect()
                can_reconnect = True

                while not self.has_interrupt():
                    self.loop_incoming()  # dispatch handle_* functions
                    self.loop_mqtt()

            except OSError as error:
                self.logger.debug("Exception: %s", error)
                self.logger.error(
                    "Connection error. Reconnect in %s sec.", reconnect_timeout
                )
                self.statistics_update()

        self.logger.info("Stopped")

    def publish_data_item(self, topic, payload):
        self.client.publish(
            self.get_topic(topic),
            payload=payload,
            qos=self.publish_qos,
            retain=self.publish_retain,
        )

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

    def handle_write_source(self, incoming, value, source_time):
        self.logger.debug(
            "'Write source' event to %s. value: %s at: %s",
            incoming.key,
            value,
            source_time,
        )
        data = incoming.pack_value(value, source_time, 1, self.origin)
        topic, payload = incoming.make_message(incoming.key, data)
        self.publish_data_item(topic, payload)
