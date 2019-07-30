import time
import pytest
import asyncio
import aiohttp
from unittest.mock import Mock
from netdef.Controllers import ConcurrentWebRequestController
from netdef.Sources import ConcurrentWebRequestSource

NAME = "ConcurrentWebRequestController"
CTRL = ConcurrentWebRequestController.ConcurrentWebRequestController

class SRC(ConcurrentWebRequestSource.ConcurrentWebRequestSource):
    def testing_echo_request(self):
        html_response = (yield ConcurrentWebRequestSource.Request("GET", self.build_url("/")))
        yield ConcurrentWebRequestSource.Result(html_response)

def get_event_loop(self):
    return asyncio.get_event_loop()
CTRL.get_event_loop = get_event_loop

def test_init_task_limit():
    shared = Mock()
    shared.config.config.side_effect = [100, 1000]
    ctl = CTRL(NAME, shared)
    assert ctl.max_iterations == 100
    assert ctl.max_concurrent_tasks == 1000
    shared.config.config.assert_any_call(NAME, "max_iterations", 100)
    shared.config.config.assert_any_call(NAME, "max_concurrent_tasks", 1000)

@pytest.mark.asyncio
async def test_get_client_session():
    shared = Mock()
    shared.config.config.side_effect = [100, 1000]
    ctl = CTRL(NAME, shared)
    src = SRC("")
    ctl_session = ctl.get_client_session(src)
    src_session = src.get_client_session()
    
    assert ctl_session is src_session
    assert isinstance(ctl_session, aiohttp.ClientSession)

@pytest.mark.asyncio
async def test_proccess_web_request_item():
    shared = Mock()
    shared.config.config.side_effect = [100, 1000]
    ctl = CTRL(NAME, shared)
    item = SRC("")

    async def res():
        async def text():
            return "html-data-1"
        async def rel():
            return None
        resp = Mock()
        resp.text.return_value = text()
        resp.release.return_value = rel()
        return resp

    session = Mock()
    session.request.return_value = res()

    item.add_client_session(session)
    available, data = await ctl.proccess_web_request_item(
        item, "testing_echo_request", session
    )
    assert available == True
    assert data == "html-data-1"


def test_next_interval_basic():
    NI = ConcurrentWebRequestController.NextInterval
    now = 0.0
    ni = NI(now)
    ni.add(10)
    assert ni.next(now) == (10.0, 10)
    assert ni.next(now) == (20.0, 10)
    assert ni.next(now) == (30.0, 10)

    ni = NI(now)
    ni.add(4)
    ni.add(10)
    assert ni.next(now) == (4.0, 4)
    assert ni.next(now) == (8.0, 4)
    assert ni.next(now) == (10.0, 10)
    assert ni.next(now) == (12.0, 4)
    assert ni.next(now) == (16.0, 4)
    assert ni.next(now) == (20.0, 4)
    assert ni.next(now) == (20.0, 10)

    ni = NI(now)
    ni.add(1)
    ni.add(2)
    ni.add(3)
    assert ni.next(now) == (1.0, 1)
    assert ni.next(now) == (2.0, 1)
    assert ni.next(now) == (2.0, 2)
    assert ni.next(now) == (3.0, 1)
    assert ni.next(now) == (3.0, 3)
    assert ni.next(now) == (4.0, 1)
    assert ni.next(now) == (4.0, 2)
    assert ni.next(now) == (5.0, 1)
    assert ni.next(now) == (6.0, 1)
    assert ni.next(now) == (6.0, 2)
    assert ni.next(now) == (6.0, 3)


def test_next_interval_time_10():
    NI = ConcurrentWebRequestController.NextInterval
    now = time.time()
    ni = NI(now)
    ni.add(10)

    for _ in range(5):
        now += 10.0
        assert ni.next(now) == (0.0, 10)

def test_next_interval_time_5():
    NI = ConcurrentWebRequestController.NextInterval
    now = time.time()
    ni = NI(now)
    ni.add(5)

    now += 0.2
    assert ni.next(now) == (pytest.approx(4.8), 5)
    now += 5.3
    assert ni.next(now) == (pytest.approx(4.5), 5)
