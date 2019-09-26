import queue
import time
from threading import Lock
from enum import Enum

class Mode(Enum):
    FIRST = 1
    LAST = 2
    LIST_ALL = 3
    FIRST_WITH_EVENT = 4
    LAST_WITH_EVENT = 5

class Collector():
    def __init__(self, fn, wait, mode):
        self.mode = mode
        self.fn = fn
        self.wait = wait
        self.buffer = queue.Queue()
        self.lock = Lock()
        if not self.mode in (Mode.FIRST, Mode.LAST, Mode.LIST_ALL,Mode.FIRST_WITH_EVENT, Mode.LAST_WITH_EVENT):
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
            if self.mode == Mode.FIRST:
                self.fn(*_args[0])
            elif self.mode == Mode.LAST:
                self.fn(*_args[-1])
            elif self.mode == Mode.LIST_ALL:
                self.fn(*zip(*_args))
            elif self.mode in (Mode.FIRST_WITH_EVENT, Mode.LAST_WITH_EVENT):
                events = [src for arg in _args for src in arg if src.update or src.new]
                if self.mode == Mode.FIRST_WITH_EVENT:
                    self.fn(*_args[0], events)
                elif self.mode == Mode.LAST_WITH_EVENT:
                    self.fn(*_args[-1], events)


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
