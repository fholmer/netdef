import time

class Tick():
    __slots = ('_tick', 'controller')
    def __init__(self, controller):
        self.controller = controller
        self._tick = time.time()
    def tick(self):
        self._tick = time.time()
    def timediff(self):
        return round(time.time() - self._tick, 1)

