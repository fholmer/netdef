import asyncio
import time
import datetime
from itertools import repeat
import aiohttp
from netdef.Controllers import BaseAsyncController, Controllers
from netdef.Sources.BaseSource import StatusCode
from netdef.Sources.ConcurrentWebRequestSource import ConcurrentWebRequestSource, Request, Result

# this controller is in development, do not use it yet.

@Controllers.register("ConcurrentWebRequestController")
class ConcurrentWebRequestController(BaseAsyncController.BaseAsyncController):
    """
    .. danger:: Development Status :: 3 - Alpha

    Basically just a web scraper. Can scrape multiple web pages simultaneously.

    IO is handeled by this controller. The poll interval and program flow
    is implemented in `ConcurrentWebRequestSource`

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger.info("init")
        self.init_task_limit()


    def init_task_limit(self):
        "Read configuration"
        self.max_iterations = self.shared.config.config(self.name, "max_iterations", 100)
        # this lock should limit the number of simultaneous tasks
        self.max_concurrent_tasks = self.shared.config.config(self.name, "max_concurrent_tasks", 1000)
        self.access_task = asyncio.Semaphore(self.max_concurrent_tasks, loop=self.loop)


    def handle_add_source(self, incoming):
        "Add source to controller"
        self.logger.debug("'Add source' event for %s %s", incoming.key, incoming.source)
        if isinstance(incoming, ConcurrentWebRequestSource):
            self.add_source(incoming.key, incoming)
        else:
            self.logger.error("Source class not supported: %s", incoming.source)


    def handle_write_source(self, incoming, value, source_time):
        "execute a command if given value is the name of a command"
        if value in incoming.get_commands_list():
            asyncio.run_coroutine_threadsafe(self.proccess_task(incoming, value), loop=self.loop)
        else:
            self.logger.error("command not available: %s", value)


    async def loop_outgoing_until_interrupt(self):
        """
        Main async loop.

        """
        await self.enter_running_state.wait()

        if not self.has_interrupt():

            # connect_request at startup
            sources = [source for source in self.get_sources().values() if source.has_connect_request()]
            tasks = tuple((self.proccess_task(item, "get_connect_request") for item in sources))
            if tasks:
                await asyncio.gather(*tasks, loop=self.loop)

        interval_plan = NextInterval(time.time())
        for source in self.get_sources().values():
            if source.has_poll_request():
                pri = source.get_poll_request_interval()
                if pri > 0:
                    interval_plan.add(pri)
            
        while not self.has_interrupt():

            if not interval_plan.has_interval():
                return

            timeout, current_interval = interval_plan.next(time.time())

            try:
                await asyncio.wait_for(self.interrupt_loop.wait(), timeout, loop=self.loop)
            except asyncio.TimeoutError:
                pass
            
            if self.has_interrupt():
                return

            sources = [source for source in self.get_sources().values() if source.has_poll_request()]
            sources = [source for source in sources if source.get_poll_request_interval() == current_interval]
            tasks = tuple((self.proccess_task(item, "get_poll_request") for item in sources))
            if tasks:
                await asyncio.gather(*tasks, loop=self.loop)


    def run(self):
        'Main sync loop'
        self.logger.info("Running")

        # self.incoming polling synchronously in own thread
        self.loop.run_in_executor(None, self.loop_incoming_until_interrupt)
        
        # async polling of sockets
        self.loop.run_until_complete(self.loop_outgoing_until_interrupt())
        self.logger.info("Stopped")


    def get_client_session(self, item):
        """
        Returns a aiohttp session.
        Add new session to source if not found. Session will be initialized
        with basic auth and a default timeout
        """
        session = item.get_client_session()
        if not session:
            if item.has_basic_auth():
                user, passw = item.get_basic_auth()
                auth = aiohttp.BasicAuth(user, passw)
            else:
                auth = None
            timeout = aiohttp.ClientTimeout(total=item.get_client_session_timeout())
            session = aiohttp.ClientSession(
                cookie_jar=aiohttp.CookieJar(unsafe=True),
                auth=auth,
                loop=self.loop,
                timeout=timeout)
            item.add_client_session(session)
        return session


    async def proccess_web_request_item(self, item, method, session):
        "handle IO by interfacing with the sources data generator"
        available = False
        data = {}
        try:
            html_data = None

            for find_data in repeat(getattr(item, method)(), self.max_iterations):

                result = find_data.send(html_data)
                assert not result is None

                if isinstance(result, Request):
                    response = await session.request(
                        method=result.method,
                        url=result.url,
                        params=result.params,
                        data=result.data
                    )
                    html_data = await response.text()
                    await response.release()
                    available = True
                    assert isinstance(html_data, str)
                elif isinstance(result, Result):
                    data = result.result
                else:
                    raise ValueError("Excpected Request or Result. Got %s" % type(result))
        except StopIteration:
            pass
        #except aiohttp.client_exceptions.ClientResponseError as error:
        #    self.logger.error("error for %s: %s", item.key, error)
        except (ValueError, ConnectionRefusedError, OSError, asyncio.TimeoutError) as error:
            self.logger.debug("error %s", error)
        except Exception as error:
            self.logger.error("%s: %s", item.get_reference(), error)

        return available, data


    async def proccess_task(self, item, method):
        "Retrives data from web site and packs it into the source"

        if not isinstance(item, ConcurrentWebRequestSource):
            self.logger.error("source of type %s not implemented", type(item))
            return

        elif not hasattr(item, method):
            self.logger.error("method %s missing in %s", method, type(item))
            return

        session = self.get_client_session(item)
        time_begin = time.time()
        await self.access_task.acquire()

        available, data = await self.proccess_web_request_item(item, method, session)

        time_end = time.time()
        self.access_task.release()

        new_val = round(time_end - time_begin, 3), available, data
        stime =  datetime.datetime.utcnow()
        status_ok = True
        cmp_oldnew = False

        if self.update_source_instance_value(item, new_val, stime, status_ok, cmp_oldnew):
            self.send_outgoing(item)


class NextInterval():
    "Call next() to retrieve seconds to next interval, and which interval it is"
    __slots__ = ['spans', 'start']
    def __init__(self, timestamp):
        self.spans = []
        self.start = timestamp
    def has_interval(self):
        return True if self.spans else False
    def add(self, interval):
        new_span = [self.start + interval, interval]
        if not new_span in self.spans:
            self.spans.append(new_span)
    def next(self, now):
        okay_then = min(self.spans)
        when, what = okay_then  # When? What?? okay then
        if when < now: # When? now?
            when = now # When? NOW!??
        okay_then[0] = when + what # Okay then, when? what?
        return when - now, what # When? Now what?
