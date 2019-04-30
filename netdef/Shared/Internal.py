# a singleton dict for misc. stats.
from collections import OrderedDict

class Statistics():
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
