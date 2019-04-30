import asyncio
from . import BaseController, Controllers

# denne er under utvikling, altså ikke i bruk enda

#@Controllers.register("BaseAsyncParallelController")
class BaseAsyncParallelController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger.info("init")
        self.init_parallel()
        self.init_task_limit()

    def init_parallel(self):
        # egen eventloop bare for denne kontrolleren
        self.loop = asyncio.new_event_loop()
        # dette signalet mottas når program avsluttes
        self.interrupt_loop = asyncio.locks.Event(loop=self.loop)

    def init_task_limit(self):
        # denne låsen skal begrense antall samtidige oppgaver
        self.max_parallel_tasks = self.shared.config.config(self.name, "max_parallel_tasks", 1000)
        self.access_task = asyncio.Semaphore(self.max_parallel_tasks, loop=self.loop)

    def loop_incoming_until_interrupt(self):
        # denne funksjonen kjører som en vanlig blokkerende tråd i asyncio
        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene
        # her må vi fortelle asyncio at det er på tide å stoppe
        self.interrupt_loop.set()

    @asyncio.coroutine
    def loop_outgoing_until_interrupt(self):
        """ eksempel på loop som utfører corutine i parallell"""
        raise NotImplementedError
        interval = 2

        yield from asyncio.sleep(2, loop=self.loop)

        while not self.has_interrupt():

            sources = list(self.get_sources().values())
            tasks = tuple((self.parallel_task(item) for item in sources))
            yield from asyncio.gather(*tasks, loop=self.loop)
            try:
                yield from asyncio.wait_for(self.interrupt_loop.wait(), interval, loop=self.loop)
            except asyncio.TimeoutError:
                pass 

    def run(self):
        self.logger.info("Running")
        # kjører polling av self.incoming synkront i egen tråd
        self.loop.run_in_executor(None, self.loop_incoming_until_interrupt)
        # kjører async polling av sockets
        self.loop.run_until_complete(self.loop_outgoing_until_interrupt())
        self.logger.info("Stopped")

    @asyncio.coroutine
    def parallel_task(self, item):
        raise NotImplementedError
        yield from self.access_socket.acquire()
        # TODO: do something
        self.access_socket.release()
