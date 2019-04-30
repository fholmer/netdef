import logging
from . import BaseSource, Sources

log = logging.getLogger(__name__)

log.debug("Loading module")


@Sources.register("TextSource")
class TextSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.debug("init %s", self.key)
