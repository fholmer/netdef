import threading
from threading import Thread, Event
from concurrent.futures import ThreadPoolExecutor
import time
import os
import logging
from . import BaseEngine
from ..Shared.Internal import Statistics

log = logging.getLogger("ThreadedEngine")
log.info("Enter ThreadedEngine")

class ThreadedEngine(BaseEngine.BaseEngine):
    def __init__(self, shared):
        super().__init__(shared)
        self._controller_pool = {}
        self._rule_pool = {}
        self._expression_executor = None
        self._expression_executor_thread = None
        self._interrupt = Event()

    def init(self):
        self._controllers.init()
        self._rules.init()
        self._sources.init()
    
    def load(self, base_package):
        pass

    def start(self):
        time.sleep(0.1)

        log.info("Parse rules")
        for name, obj in self._rules.instances.items():
            obj.setup()
            obj.add_interrupt(self._interrupt)
            thr = Thread(target=obj.run, name=name)
            thr.start()
            self._rule_pool[name] = thr

        log.info("Start expression executor")
        self._expression_executor = ExpressionExecutor("ExpressionExecutor", self.shared)
        self._expression_executor.add_interrupt(self._interrupt)
        self._expression_executor_thread = Thread(
            target=self._expression_executor.run,
            name="ExpressionExecutor"
        )
        self._expression_executor_thread.start()

        log.info("Start controllers")
        for name, obj in self._controllers.instances.items():
            obj.add_interrupt(self._interrupt)
            thr = Thread(target=obj.run, name=name)
            thr.start()
            self._controller_pool[name] = thr

    @staticmethod
    def block():
        log.info("Wait for interrupt")
        try:
            while 1:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def stop(self):
        log.info("Send terminate interrupt")
        self._interrupt.set()
    
    def wait(self):
        ct = threading.current_thread()
        for thread in threading.enumerate():
            if not thread is ct:
                if not thread.daemon:
                    thread.join()

class ExpressionExecutor(BaseEngine.BaseExpressionExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        max_workers = (os.cpu_count() or 1) * 10
        max_workers = self.shared.config.config(self.name, "max_workers", max_workers)

        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.future_pool = []

        if Statistics.on:
            Statistics.set(self.name + ".threadpool.max_workers.count", max_workers)

    def run(self):
        log.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene
            self.loop_futures()
        self.thread_pool.shutdown(wait=True)
        log.info("Stopped")

    def handle_run_expression(self, source_item, expressions):
        for expression in expressions:
            args = expression.get_args(source_item)
            kwargs = expression.get_kwargs()
            #debuggingtriks: expression.execute(args, kwargs)
            self.future_pool.append(
                (self.thread_pool.submit(expression.execute, args, kwargs), expression.filename)
            )
    def loop_futures(self):
        #while not self.has_interrupt():
        if Statistics.on:
            Statistics.set(self.name + ".threadpool.workers.count", len(self.future_pool))

        for future, filename in self.future_pool:
            if future.done():
                self.future_pool.remove((future, filename))
                returned_exception = future.exception()
                if returned_exception:
                    log.error("Exception in %s", filename)
                    log.exception(returned_exception)
