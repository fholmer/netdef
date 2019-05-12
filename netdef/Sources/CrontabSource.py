import logging
from netdef.Sources import BaseSource, Sources

log = logging.getLogger(__name__)

log.debug("Loading module")

@Sources.register("CrontabSource")
class CrontabSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.debug("init %s", self.key)
