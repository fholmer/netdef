# a singleton dict for misc. stats.
from collections import OrderedDict

class Statistics():
    """
    A singleton class to store statistics as key-value pair.
    Can be turned off for performance or security.

    Can be imported from Rules, Controllers and Expressions.

    Example::

        import psutil
        from netdef.Shared.Internal import Statistics
        from netdef.Sources.SystemMonitorSource import bytes2human

        if Statistics.on:
            uss = psutil.Process().memory_full_info().uss
            Statistics.set("process.memory.startup", bytes2human(uss))


    """
    on = True
    statistics = OrderedDict()
    @staticmethod
    def set(key, value):
        Statistics.statistics[key] = value
    @staticmethod
    def get(key):
        return Statistics.statistics[key]
    @staticmethod
    def get_dict():
        return Statistics.statistics
