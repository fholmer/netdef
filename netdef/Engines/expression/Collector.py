import queue
import time
from threading import Lock
from enum import Enum

class Mode(Enum):
    LIST_ALL = 1

class Collector():
    def __init__(self, fn, wait, mode):
        self.mode = mode
        self.fn = fn
        self.wait = wait
        self.buffer = queue.Queue()
        self.lock = Lock()
        if self.mode != Mode.LIST_ALL:
            raise NotImplementedError

    def __call__(self, *args):
        _lock = self.lock.acquire(blocking=False)
        self.buffer.put(args)
        if _lock:
            time.sleep(self.wait)
            _args = []
            while not self.buffer.empty():
                _args.append(self.buffer.get_nowait())
            self.lock.release()
            self.fn(*zip(*_args))

def collect(wait, mode):
    """
    A decorator for expressions.

    Usage::

        from netdef.Engines.expression.Collector import collect, Mode

        @collect(wait=0.1, mode=Mode.LIST_ALL)
        def expression(c1, c2, c3):
            pass

    """
    def fn(func):
        _fn = Collector(func, wait, mode)
        return _fn
    return fn
