from . import BaseSource, Sources
from ..Interfaces.DefaultInterface import DefaultInterface

@Sources.register("XmlRpcMethodCallSource")
class XmlRpcMethodCallSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface

    def make_rpc_request(self, value):
        method, *arguments = value
        return method, arguments
    
    def parse_rpc_response(self, value):
        return value

    def poll_request(self):
        return self.key.split(";")

    @staticmethod
    def can_unpack_subitems(value):
        return False

    @staticmethod
    def unpack_subitems(value):
        yield None

