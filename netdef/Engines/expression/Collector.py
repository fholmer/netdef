import queue
import time
from enum import Enum
from threading import Lock


class Mode(Enum):
    "collector modes"
    FIRST = 1
    "Use arguments from the first call"
    LAST = 2
    "Use arguments from the last call"
    LIST_ALL = 3
    "Convert arguments to lists with every call"
    FIRST_WITH_EVENT = 4
    "Use arguments from the first call and an additional argument called event"
    LAST_WITH_EVENT = 5
    "Use arguments from the last call and an additional argument called event"


class Collector:
    """
    Takes a function but does not call it right away. After the given wait
    time has elapsed the function is called based on the given mode.

    :param callable fn: a function or callable
    :param float wait: seconds to wait
    :param Mode mode: how to call the callable
    """

    def __init__(self, fn, wait, mode):
        self.mode = mode
        self.fn = fn
        self.wait = wait
        self.buffer = queue.Queue()
        self.lock = Lock()
        if not self.mode in (
            Mode.FIRST,
            Mode.LAST,
            Mode.LIST_ALL,
            Mode.FIRST_WITH_EVENT,
            Mode.LAST_WITH_EVENT,
        ):
            raise NotImplementedError

    def __call__(self, *args):
        """
        Add arguments to a queue. Only the first call will acquire
        :attr:`self.lock` and sleep until wait time has elapsed. After sleep
        the arguments in queue is used to call the function :attr:`self.fn`
        based on the chosen mode.
        """
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
