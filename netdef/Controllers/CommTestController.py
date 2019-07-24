import time
import datetime
import asyncio
from . import BaseAsyncController, Controllers
from ..Sources.BaseSource import StatusCode
from .ping import ping

@Controllers.register("CommTestController")
class CommTestController(BaseAsyncController.BaseAsyncController):
    """
    .. tip:: Development Status :: 5 - Production/Stable

    CommTestController will start tcp-polling and 

    """
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
       
        # denne låsen skal begrense antall åpne forbindelser
        self.access_socket = asyncio.Semaphore(self.max_concurrent_sockets, loop=self.loop)


    async def loop_outgoing_until_interrupt(self):
        """
        Main coroutine. loops until interrupt is set.
        """

        await asyncio.sleep(2, loop=self.loop)

        while not self.has_interrupt():
            # poller på self.intervall
            sources = list(self.get_sources().values())
            tasks = tuple((self.commtest_tcp_connect(item) for item in sources))
            await asyncio.gather(*tasks, loop=self.loop)
            try:
                await asyncio.wait_for(self.interrupt_loop.wait(), self.interval, loop=self.loop)
            except asyncio.TimeoutError:
                pass 


    def run(self):
        """
        Main thread loop. Will exit when receiving interrupt signal
        Sets up 
        """
        self.logger.info("Running")

        # kjører polling av self.incoming synkront i egen tråd
        self.loop.run_in_executor(None, self.loop_incoming_until_interrupt)

        # kjører async polling av sockets
        self.loop.run_until_complete(self.loop_outgoing_until_interrupt())
        self.logger.info("Stopped")


    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)


    async def commtest_tcp_connect(self, item):
        if hasattr(item, "unpack_host_and_port"):
            host, port = item.unpack_host_and_port()

            await self.access_socket.acquire()

            prev_st = item.status_code
            time_begin = time.time()

            # async ping
            if self.test_type == "ping":
                try:
                    delay = await ping.async_ping(host, timeout=self.timeout)
                    delay = round(delay, 3)
                    available = True
                except TimeoutError:
                    available = False
                    delay = round(time.time() - time_begin, 3)
                    
            # test tcp port
            else:
                available = await ping.tcp_port_test_async(host, port, self.timeout, loop=self.loop)
                delay = round(time.time() - time_begin, 3)

            self.access_socket.release()

            item.get = delay, available
            item.source_time = datetime.datetime.utcnow()

            if prev_st == StatusCode.NONE:
                item.status_code = StatusCode.INITIAL
            else:
                item.status_code = StatusCode.GOOD

            self.send_outgoing(item)
