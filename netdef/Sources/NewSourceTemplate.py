from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.DefaultInterface import DefaultInterface

@Sources.register("NewSourceTemplate")
class NewSourceTemplate(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface
    
    # TODO: add a address for your new controller
    def unpack_address(self):
        return self.key
