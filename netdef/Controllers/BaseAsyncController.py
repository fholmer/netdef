import asyncio
from netdef.Controllers import BaseController, Controllers

# this controller is in development, do not use it yet.

class BaseAsyncController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.init_asyncio()

    def init_asyncio(self):
        # egen eventloop bare for denne kontrolleren
        self.loop = asyncio.new_event_loop()

        # dette signalet mottas når program avsluttes
        self.interrupt_loop = asyncio.locks.Event(loop=self.loop)

    def loop_incoming_until_interrupt(self):
        # denne funksjonen kjører som en vanlig blokkerende tråd i asyncio
        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene

        # her må vi fortelle asyncio at det er på tide å stoppe
        self.interrupt_loop.set()

    async def run_async_on_interrupt(self, callback):
        await self.interrupt_loop.wait()
        await callback()

    def run(self):
        raise NotImplementedError
