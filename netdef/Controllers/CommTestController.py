import time
import datetime
import asyncio
from . import BaseController, Controllers
from ..Sources.BaseSource import StatusCode
from .ping import ping

@Controllers.register("CommTestController")
class CommTestController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger.info("init")
        config = self.shared.config.config
        self.interval = config(self.name, "interval", 10)
        self.timeout = config(self.name, "timeout", 2)
        # hvor mange forbindelser kan være åpne samtidig?
        self.max_concurrent_sockets = config(self.name, "max_concurrent_sockets", 1000)

        # ping: async ping
        # tcpip: async tcpip socket connect
        self.test_type = config(self.name, "test_type", "tcpip")

        self.loop = asyncio.new_event_loop()
        
        # denne låsen skal begrense antall åpne forbindelser
        self.access_socket = asyncio.Semaphore(self.max_concurrent_sockets, loop=self.loop)

        # dette signalet mottas når program avsluttes
        self.interrupt_loop = asyncio.locks.Event(loop=self.loop)

    def loop_incoming_until_interrupt(self):
        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene
        self.interrupt_loop.set()

    @asyncio.coroutine
    def loop_outgoing_until_interrupt(self):
        yield from asyncio.sleep(2, loop=self.loop)

        while not self.has_interrupt():
            # poller på self.intervall
            sources = list(self.get_sources().values())
            tasks = tuple((self._commtest_tcp_connect(item) for item in sources))
            yield from asyncio.gather(*tasks, loop=self.loop)
            try:
                yield from asyncio.wait_for(self.interrupt_loop.wait(), self.interval, loop=self.loop)
            except asyncio.TimeoutError:
                pass 

    def run(self):
        self.logger.info("Running")
        # kjører polling av self.incoming synkront i egen tråd
        self.loop.run_in_executor(None, self.loop_incoming_until_interrupt)
        # kjører async polling av sockets
        self.loop.run_until_complete(self.loop_outgoing_until_interrupt())
        self.logger.info("Stopped")

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

    @asyncio.coroutine
    def _commtest_tcp_connect(self, item):
        if hasattr(item, "unpack_host_and_port"):
            host, port = item.unpack_host_and_port()

            yield from self.access_socket.acquire()

            prev_st = item.status_code
            time_begin = time.time()

            # async ping
            if self.test_type == "ping":
                try:
                    delay = yield from ping.async_ping(host, timeout=self.timeout)
                    delay = round(delay, 3)
                    available = True
                except TimeoutError:
                    available = False
                    delay = round(time.time() - time_begin, 3)
                    
            # test tcp port
            else:
                available = yield from ping.tcp_port_test_async(host, port, self.timeout, loop=self.loop)
                delay = round(time.time() - time_begin, 3)

            self.access_socket.release()

            item.get = delay, available
            item.source_time = datetime.datetime.utcnow()

            if prev_st == StatusCode.NONE:
                item.status_code = StatusCode.INITIAL
            else:
                item.status_code = StatusCode.GOOD

            self.send_outgoing(item)
