import logging
import time
import datetime
import psutil
import threading
from netdef.Controllers import BaseController, Controllers
from netdef.Sources.BaseSource import StatusCode
from netdef.Shared.Internal import Statistics

# import my supported sources
from ..Sources.SystemMonitorSource import bytes2human, SystemMonitorSource, SystemMonitorByteSource, SystemMonitorPercentSource

def get_vm():
    return psutil.virtual_memory()

def get_proc():
    return psutil.Process()

def statistics_update(item):
    if Statistics.on:
        Statistics.set(
            item.key,
            "{} ({})".format(
                item.get_value_and_unit(),
                item.source_time.strftime("%Y.%m.%d %H:%M:%S")
            )
        )

class DataItem():
    __slots__ = ('key', 'source_type', 'interval', 'func', 'next')
    def __init__(self, source_type, key, interval, func):
        self.source_type = source_type
        self.key = key
        self.interval = interval
        self.func = func
        self.next = 0

    def get_value(self):
        return self.func()

    def ready(self):
        now = time.time()
        if now >= self.next:
            self.next = (now + self.interval)
            return True
        return False

def get_data_items_dict(mempoll, cpupoll, poll):
    NO = SystemMonitorSource
    BY = SystemMonitorByteSource
    PE = SystemMonitorPercentSource
    items = [
        DataItem(PE, "sysmon.cpu.percent", cpupoll, lambda: psutil.cpu_percent(interval=1)),
        DataItem(PE, "sysmon.memory.percent", mempoll, lambda: get_vm().percent),
        DataItem(BY, "sysmon.memory.total", mempoll, lambda: get_vm().total),
        DataItem(BY, "sysmon.memory.available", mempoll, lambda: get_vm().available),
        DataItem(BY, "sysmon.memory.free", mempoll, lambda: get_vm().free),
        DataItem(BY, "sysmon.memory.used", mempoll, lambda: get_vm().used),
        DataItem(NO, "sysmon.threads.total", poll, lambda: threading.active_count()),
        DataItem(NO, "process.pid", poll, lambda: get_proc().pid),
        DataItem(PE, "process.cpu.percent", cpupoll, lambda: get_proc().cpu_percent(interval=1)),
        DataItem(PE, "process.memory.percent", mempoll, lambda: get_proc().memory_percent()),
        DataItem(BY, "process.memory.current", mempoll, lambda: get_proc().memory_full_info().uss),
        DataItem(NO, "process.open.files.count", poll, lambda: len(get_proc().open_files()))
    ]
    return {data.key: data for data in items}

@Controllers.register("SystemMonitorController")
class SystemMonitorController(BaseController.BaseController):
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        self.oldnew = self.shared.config.config(self.name, "oldnew_comparision", 0)
        self.memory_poll_interval = self.shared.config.config(self.name, "memory_poll_interval", 600)
        self.cpu_poll_interval = self.shared.config.config(self.name, "cpu_poll_interval", 10)
        self.poll_interval = self.shared.config.config(self.name, "general_poll_interval", 10)

        self.data_items = get_data_items_dict(
            self.memory_poll_interval,
            self.cpu_poll_interval,
            self.poll_interval
        )
        self.internal_sources = {key: data.source_type(key=key) for key, data in self.data_items.items()}

    def run(self):
        self.logger.info("Running")
        if Statistics.on:
            uss = psutil.Process().memory_full_info().uss
            Statistics.set("process.memory.startup", bytes2human(uss))

        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene
            self.poll_data()

        self.logger.info("Stopped")

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)

    def handle_write_source(self, incoming, value, source_time):
        self.logger.debug("'Write source' event to %s. value: %s at: %s", incoming.key, value, source_time)

    def poll_data(self):
        stime = datetime.datetime.utcnow()
        status_ok = True
        for dataitem in self.data_items.values():
            if dataitem.ready():
                value = dataitem.get_value()
                internal_item = self.internal_sources[dataitem.key]
                self.update_source_instance_value(internal_item, value, stime, status_ok, self.oldnew)
                statistics_update(internal_item)
                if self.has_source(dataitem.key):
                    self.send_datachange(dataitem.key, value, stime, True)

    def send_datachange(self, source_key, value, stime, status_ok):
        item = self.get_source(source_key)
        if self.update_source_instance_value(item, value, stime, status_ok, self.oldnew):
            self.send_outgoing(item)
