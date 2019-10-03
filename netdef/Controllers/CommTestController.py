import time
import datetime
import asyncio
import encodings.idna
from . import BaseAsyncController, Controllers
from ..Sources.BaseSource import StatusCode
from .ping import ping

@Controllers.register("CommTestController")
class CommTestController(BaseAsyncController.BaseAsyncController):
    """
    .. tip:: Development Status :: 5 - Production/Stable

    This class will send TCP or ICMP ping requests based on sources received in
    ADD_SOURCE messages and store the result into given sources. When result
    is stored into a source this class will send the changed source in a
    RUN_EXPRESSION message to the source's rule.

    :param str name: Name of controller
    :param netdef.Shared shared: Instance of applications shared object.

    Configuration:
        * **timeout** -- Connection timeout in seconds
        * **interval** -- Poll interval in seconds
        * **test_type** -- Available types: [tcpip, ping]
        * **max_concurrent_sockets** -- Max number of simultaneous
          open sockets.
        * **disable** -- If disabled this controller will enter running
          state but all messages will be discarded.
    
    Defaults:
        .. code-block:: ini

            [CommTestController]
            timeout = 2
            interval = 10
            test_type = tcpip
            max_concurrent_sockets = 1000
            disable = 0

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger.info("init")
        config = self.shared.config.config
        self.interval = config(self.name, "interval", 10)
        self.timeout = config(self.name, "timeout", 2)
        self.disable = config(self.name, "disable", 0)

        if self.disable:
            self.logger.info("Disabled. All messages will be discarded.")

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

        await self.enter_running_state.wait()

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

        if self.disable:  # to disable: empty queue by calling self.fetch_one_incoming
            while not self.has_interrupt():
                messagetype, incoming = self.fetch_one_incoming()
                if messagetype and messagetype == self.messagetypes.TICK:
                    self.handle_tick(incoming)
        else:
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

            new_val = delay, available
            stime = datetime.datetime.utcnow()
            status_ok = True
            cmp_oldnew = False

        if self.update_source_instance_value(item, new_val, stime, status_ok, cmp_oldnew):
            self.send_outgoing(item)
