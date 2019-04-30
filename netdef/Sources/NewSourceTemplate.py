import logging
from . import BaseSource, Sources
from ..Interfaces.DefaultInterface import DefaultInterface

log = logging.getLogger(__name__)

log.debug("Loading module")

@Sources.register("NewSourceTemplate")
class NewSourceTemplate(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.debug("init %s", self.key)

        self.interface = DefaultInterface
    
    # TODO: add a address for your new controller
    def unpack_address(self):
        return self.key
