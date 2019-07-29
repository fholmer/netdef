import asyncio
from netdef.Controllers import BaseController, Controllers

# this controller is in development, do not use it yet.

class BaseAsyncController(BaseController.BaseController):
    """
    .. tip:: Development Status :: 5 - Production/Stable

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.init_asyncio()
    
    def init_asyncio(self):
        # egen eventloop bare for denne kontrolleren
        self.loop = self.get_event_loop()

        # dette signalet mottas når program avsluttes
        self.interrupt_loop = asyncio.locks.Event(loop=self.loop)
        self.enter_running_state = asyncio.locks.Event(loop=self.loop)

    def get_event_loop(self):
        return asyncio.new_event_loop()

    def loop_incoming_until_interrupt(self):
        # denne funksjonen kjører som en vanlig blokkerende tråd i asyncio
        while not self.has_interrupt():
            self.loop_incoming() # dispatch handle_* functions

        # her må vi fortelle asyncio at det er på tide å stoppe
        async def set_event(event):
            event.set()
        asyncio.run_coroutine_threadsafe(set_event(self.interrupt_loop), loop=self.loop)

    def handle_app_state_running(self):
        async def set_event(event):
            event.set()
        asyncio.run_coroutine_threadsafe(set_event(self.enter_running_state), loop=self.loop)
        super().handle_app_state_running()
        
    async def run_async_on_interrupt(self, callback):
        await self.interrupt_loop.wait()
        await callback()

    def run(self):
        """
        Override this function in controller. Example:

        .. code-block:: python

            def run(self):
                self.logger.info("Running")

                some_client = SomeAsyncioClient()

                # Start polling of the blocking incoming queue in a thread executor
                self.loop.run_in_executor(None, self.loop_incoming_until_interrupt)

                # TODO: define a coroutine that stops your async client when called.
                async def stop_some_client():
                    await some_client.stop()

                # register coroutine to be run at interrupt / shutdown 
                self.loop.create_task(self.run_async_on_interrupt(stop_some_client))

                # TODO: start your client coroutine
                self.loop.run_until_complete(some_client.start())

                self.logger.info("Stopped")
        """
        raise NotImplementedError
