from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.DefaultInterface import DefaultInterface

@Sources.register("SubprocessSource")
class SubprocessSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface

    def get_command_and_args(self, args=None):
        if args:
            return self.key + " " + args
        else:
            return self.key
