import logging
import time
from netdef.Sources import BaseSource, Sources
from netdef.Interfaces.ConcurrentWebRequestInterface import ConcurrentWebRequestInterface

@Sources.register("ConcurrentWebRequestSource")
class ConcurrentWebRequestSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = ConcurrentWebRequestInterface
        self._session = None
        self.logger = logging.getLogger("ConcurrentWebRequestSource")
        self.logger.debug("init %s", self.key)
        self.basic_auth_user = None
        self.basic_auth_pass = None
        self.url_scheme = "http://"
        self.base_url = None
        self.parse_url(self.key)

    def parse_url(self, url):
        if "://" in url:
            self.url_scheme, url = url.split("://", 1)
            self.url_scheme += "://"

        if "@" in url:
            login, url = url.split("@", 1)

            if ":" in login:
                self.basic_auth_user, self.basic_auth_pass = login.split(":", 1)
                
        self.base_url = url

    def get_client_session(self):
        return self._session
    
    def add_client_session(self, session):
        self._session = session

    def get_client_session_timeout(self):
        return 2
    
    def get_commands_list(self):
        return []

    def has_basic_auth(self):
        return (not self.basic_auth_user is None)

    def get_basic_auth(self):
        return self.basic_auth_user, self.basic_auth_pass
    
    def build_url(self, url):
        return "{}{}{}".format(self.url_scheme, self.base_url, url)

    def get_start_url(self):
        return self.build_url("/")

    def has_connect_request(self):
        return False

    def get_connect_request(self):
        raise NotImplementedError
    
    def has_poll_request(self):
        return False

    def get_poll_request_interval(self):
        raise NotImplementedError

    def get_poll_request(self):
        raise NotImplementedError

class Request():
    __slots__ = ['method', 'url', 'params', 'data']
    def __init__(self, method, url, params=None, data=None):
        self.method = method
        self.url = url
        self.params = params
        self.data = data

    def __repr__(self):
        return " ".join((self.method, self.url))

class Result():
    __slots__ = ['result']
    def __init__(self, result):
        self.result = result
