import logging
from . import FloatSource, Sources
from ..Interfaces import CommTestInterface

log = logging.getLogger(__name__)

log.debug("Loading module")

@Sources.register("CommTestSource")
class CommTestSource(FloatSource.FloatSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.debug("init %s", self.key)
        self.interface = CommTestInterface.CommTestInterface

    def unpack_host_and_port(self):
        addr = self.key
        if "@" in addr:
            _, addr = addr.split("@", 1)
        if "://" in addr:
            _, addr = addr.split("://", 1)
            
        if ":" in addr:
            host, port = addr.split(":")
            return host, int(port)
        else:
            return addr, 80
