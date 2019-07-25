import asyncio
from . import BaseAsyncController, Controllers

# this controller is in development, do not use it yet.

#@Controllers.register("BaseAsyncParallelController")
class BaseAsyncParallelController(BaseAsyncController.BaseAsyncController):
    """
    .. danger:: Development Status :: 3 - Alpha

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger.info("init")
        self.init_task_limit()

    def init_task_limit(self):
        # denne låsen skal begrense antall samtidige oppgaver
        self.max_parallel_tasks = self.shared.config.config(self.name, "max_parallel_tasks", 1000)
        self.access_task = asyncio.Semaphore(self.max_parallel_tasks, loop=self.loop)

    async def loop_outgoing_until_interrupt(self):
        """
        Main async loop.
        Clients need to implement this function.

        Example::

            interval = 2

            await asyncio.sleep(2, loop=self.loop)

            while not self.has_interrupt():

                sources = list(self.get_sources().values())
                tasks = tuple((self.parallel_task(item) for item in sources))
                await asyncio.gather(*tasks, loop=self.loop)
                try:
                    await asyncio.wait_for(self.interrupt_loop.wait(), interval, loop=self.loop)
                except asyncio.TimeoutError:
                    pass 

        """
        #eksempel på loop som utfører corutine i parallell
        raise NotImplementedError

    def run(self):
        'Main sync loop'
        self.logger.info("Running")
        # kjører polling av self.incoming synkront i egen tråd
        self.loop.run_in_executor(None, self.loop_incoming_until_interrupt)
        # kjører async polling av sockets
        self.loop.run_until_complete(self.loop_outgoing_until_interrupt())
        self.logger.info("Stopped")

    async def parallel_task(self, item):
        """
        Clients need to implement this function.

        Example::

            await self.access_socket.acquire()
            # TODO: do something
            self.access_socket.release()

        """
        raise NotImplementedError
