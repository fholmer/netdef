from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.DefaultInterface import DefaultInterface

def setup(shared):
    SubprocessSource.DEFAULT_INTERVAL = shared.config.config(
        "SubprocessSource",
        "default_poll_interval",
        SubprocessSource.DEFAULT_INTERVAL,
    )

@Sources.register("SubprocessSource")
class SubprocessSource(BaseSource.BaseSource):
    DEFAULT_INTERVAL = 10
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface

    def get_command_and_args(self, args=None):
        "Get command and argument to run"
        if args:
            return self.key + " " + args
        else:
            return self.key

    def parse_stdout_response(self, value):
        "Implement parsing function"
        return value

    def has_initial_poll(self):
        return self.has_poll_interval()

    def has_poll_interval(self):
        return True

    def get_poll_interval(self):
        return self.DEFAULT_INTERVAL

    @staticmethod
    def can_unpack_subitems(value):
        "Returns False, cannot unpack subitems"
        return False

    @staticmethod
    def unpack_subitems(value):
        "Yields None, cannot unpack subitems"
        yield None
