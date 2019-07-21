import json
import pickle
import datetime
from urllib import parse

class AbstractBase():
    __slots__ = ('key', 'extension')
    def __init__(self, key, extension):
        self.key = key
        self.extension = extension

    def _to_kwargs(self):
        raise NotImplementedError

    @staticmethod
    def _make_kwargs(key=''):
        raise NotImplementedError

    def _get_uri_scheme_path_and_query(self):
        raise NotImplementedError
    
    def to_kwargs(self):
        return self._to_kwargs()

    @classmethod
    def from_uri(cls, uri):
        uri = parse.urlsplit(uri)
        qsl = parse.parse_qsl(uri.query)
        
        kwargs = cls._make_kwargs(uri.path)
        
        for key, value in qsl:
            if key in cls.__slots__[1:-1]:
                kwargs[key] = value
            else:
                kwargs["extension"][key] = value
        return cls(**kwargs)

    def to_uri(self):
        scheme, key, query = self._get_uri_scheme_path_and_query()
        uri = parse.SplitResult(
            scheme, "", key, parse.urlencode(query).replace("&", ";"), ""
        )
        return uri.geturl()

    def to_json(self):
        return json.dumps(self._to_kwargs())

    @classmethod
    def from_json(cls, json_str):
        kwargs = json.loads(json_str)
        return cls(**kwargs)

    def to_pickle(self):
        return pickle.dumps(self._to_kwargs())

    @classmethod
    def from_pickle(cls, pickle_bytes):
        kwargs = pickle.loads(pickle_bytes)
        return cls(**kwargs)


class DataMessage(AbstractBase):
    __slots__ = ('key', 'value', 'source_time', 'status_code', 'origin', 'extension')
    def __init__(self, key, value, source_time, status_code, origin, extension):
        self.key = key
        self.value = value
        self.source_time = source_time
        self.status_code = status_code
        self.origin = origin
        self.extension = extension

    def __repr__(self):
        return "DataMessage(key={}, value={}, source_time={}, status_code={}, origin={}, extension={})".format(
            self.key, self.value, self.source_time, self.status_code, self.origin, self.extension
        )

    @staticmethod
    def is_uri(uri):
        return uri.startswith(("message:", "msg:", "uri:"))

    @classmethod
    def from_uri(cls, uri):
        if not cls.is_uri(uri):
            raise ValueError("expected 'uri:', 'message:' or 'msg:' URI, got {}".format(uri))
        return super().from_uri(uri)
    
    def _get_uri_scheme_path_and_query(self):
        query = {}
        query.update(self.extension)
        query['value'] = self.value
        query['source_time'] = self.source_time
        query['status_code'] = self.status_code
        query['origin'] = self.origin
        return "msg", self.key, query

    def _to_kwargs(self):
        kwargs = {
           'key': self.key,
           'value': self.value,
           'source_time': self.source_time,
           'status_code': self.status_code,
           'origin': self.origin,
           'extension': self.extension
        }
        return kwargs
    
    @staticmethod
    def _make_kwargs(key=''):
        kwargs = {
            'key' : key,
            'value' : '',
            'source_time' : '',
            'status_code' : '',
            'origin': '',
            'extension' : {}
        }
        return kwargs

class DataDefinition(AbstractBase):
    __slots__ = ('key', 'default', 'datatype', 'access', 'extension')
    def __init__(self, key, default, datatype, access, extension):
        self.key = key
        self.default = default
        self.datatype = datatype
        self.access = access
        self.extension = extension
    
    def __repr__(self):
        return "DataDefinition(key={}, default={}, datatype={}, access={}, extension={})".format(
            self.key, self.default, self.datatype, self.access, self.extension
        )
    
    @staticmethod
    def is_uri(uri):
        return uri.startswith(("definition:", "def:", "uri:"))

    @classmethod
    def from_uri(cls, uri):
        if not cls.is_uri(uri):
            raise ValueError("expected 'uri:', 'definition:' or 'def:' URI, got {}".format(uri))
        return super().from_uri(uri)
    
    def _get_uri_scheme_path_and_query(self):
        query = {}
        query.update(self.extension)
        query['default'] = self.default
        query['datatype'] = self.datatype
        query['access'] = self.access
        return 'def', self.key, query

    def _to_kwargs(self):
        kwargs = {
           'key': self.key,
           'default': self.default,
           'datatype': self.datatype,
           'access': self.access,
           'extension': self.extension
        }
        return kwargs

    @staticmethod
    def _make_kwargs(key=''):
        kwargs = {
            'key' : key,
            'default' : '',
            'datatype' : '',
            'access' : 'rw',
            'extension' : {}
        }
        return kwargs
