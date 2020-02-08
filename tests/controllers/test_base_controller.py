import datetime
import queue
from unittest.mock import Mock

import pytest

from netdef.Controllers import BaseController
from netdef.Shared.SharedQueues import MessageType
from netdef.Sources.BaseSource import BaseSource, StatusCode


def test_basics():
    # setup
    incoming = Mock()
    incoming.get.side_effect = [(MessageType.ADD_SOURCE, "src1"), queue.Empty()]
    shared = Mock()
    shared.queues.get_messages_to_controller.return_value = incoming
    shared.queues.MessageType = MessageType

    interrupt = Mock()
    interrupt.is_set.return_value = False

    ctr = BaseController.BaseController("test", shared)
    ctr.add_interrupt(interrupt)

    # test run

    with pytest.raises(NotImplementedError):
        ctr.run()

    # test fetch_one_incoming

    item = ctr.fetch_one_incoming()
    assert item == (MessageType.ADD_SOURCE, "src1")

    item = ctr.fetch_one_incoming()
    assert item == (None, None)

    # send_outgoing

    ctr.send_outgoing(BaseSource(key="src2", rule="r2"))
    msg_t, rule2, src2 = shared.queues.send_message_to_rule.call_args[0]
    assert msg_t == MessageType.RUN_EXPRESSION
    assert rule2 == "r2"
    assert src2.key == "src2"


def test_update_source_instance_value_is_none():
    # update_source_instance_value
    src = BaseSource()
    res = BaseController.BaseController.update_source_instance_value(
        source_instance=src, value=0, stime=None, status_ok=True, oldnew_check=False
    )
    assert res == True
    assert src.get == 0
    assert src.source_time == None
    assert src.status_code == StatusCode.INITIAL


def test_update_source_instance_value_is_good():
    # update_source_instance_value
    src = BaseSource()
    src.get = 0
    src.status_code = StatusCode.INITIAL
    res = BaseController.BaseController.update_source_instance_value(
        source_instance=src, value=0, stime=None, status_ok=True, oldnew_check=False
    )
    assert res == True
    assert src.get == 0
    assert src.source_time == None
    assert src.status_code == StatusCode.GOOD


def test_update_source_instance_value_is_invalid():
    # update_source_instance_value
    src = BaseSource()
    src.get = 0
    src.status_code = StatusCode.INITIAL
    res = BaseController.BaseController.update_source_instance_value(
        source_instance=src, value=0, stime=None, status_ok=False, oldnew_check=False
    )
    assert res == True
    assert src.get == 0
    assert src.source_time == None
    assert src.status_code == StatusCode.INVALID


def test_loop_incoming():
    # setup
    now = datetime.datetime.utcnow()
    hdl_tick = (MessageType.TICK, BaseSource("tick"))
    hdl_add_source = (MessageType.ADD_SOURCE, BaseSource("add_source"))
    hdl_write_source = (
        MessageType.WRITE_SOURCE,
        (BaseSource("write_source"), 0.11, now),
    )
    hdl_add_parser = (MessageType.ADD_PARSER, BaseSource("add_parser"))

    incoming = Mock()
    incoming.get.side_effect = [
        hdl_tick,
        hdl_add_source,
        hdl_write_source,
        hdl_add_parser,
        queue.Empty(),
    ]
    shared = Mock()
    shared.queues.get_messages_to_controller.return_value = incoming
    shared.queues.MessageType = MessageType

    interrupt = Mock()
    interrupt.is_set.side_effect = [False, False, False, False, False, True]

    class Ctr(BaseController.BaseController):
        def handle_tick(self, incoming):
            assert incoming.key == "tick"
            incoming.tick = Mock()
            incoming.value = 123
            super().handle_tick(incoming)
            assert incoming.tick.called

        def handle_add_source(self, incoming):
            assert incoming.key == "add_source"
            incoming.value = 234

        def handle_write_source(self, incoming, value, source_time):
            assert incoming.key == "write_source"
            assert value == 0.11
            assert isinstance(source_time, datetime.datetime)
            incoming.value = 345

        def handle_add_parser(self, incoming):
            assert incoming.key == "add_parser"
            incoming.value = 456

    ctr = Ctr("Ctrl", shared)
    ctr.add_interrupt(interrupt)

    # check sources is set up

    assert hdl_tick[1].value == None
    assert hdl_add_source[1].value == None
    assert hdl_write_source[1][0].value == None
    assert hdl_add_parser[1].value == None

    # test loop_incoming

    ctr.loop_incoming()

    # check everything was called

    assert hdl_tick[1].value == 123
    assert hdl_add_source[1].value == 234
    assert hdl_write_source[1][0].value == 345
    assert hdl_add_parser[1].value == 456
