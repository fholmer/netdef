import logging
from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.DefaultInterface import DefaultInterface

log = logging.getLogger(__name__)

log.debug("Loading module")

@Sources.register("ZmqDataAccessSource")
class ZmqDataAccessSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.debug("init %s", self.key)

        self.interface = DefaultInterface
    
    def unpack_address(self):
        return self.key

    def pack_address(self, addr):
        return addr
