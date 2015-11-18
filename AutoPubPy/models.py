from abc import ABCMeta, abstractmethod
import collections
import copy
import json
from wstools.pubsub import Publisher, publish

class wsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSONable):
            return obj._container
        return super(wsEncoder, self).default(obj)


json_encoder = wsEncoder(ensure_ascii = False)

def is_JSONable(obj, encoder=json_encoder):
    try:
        encoded_string = json_encoder.encode(obj)
    except Exception as e:
        return False
    return True

class MetaJSON(ABCMeta):
    """An object that works."""

    @abstractmethod
    def as_JSON(self):
        """Returns the object in it's json form."""

class JSONable(object):
    __metaclass__ = MetaJSON


class JSONDict(Publisher, collections.MutableMapping, JSONable):
    "test doc"
    topic = 'com.dict'
    _protect_attributes = ['_propagate', '_subscribers', '_topic_prefix', '_container']
    def __init__(self, *args, **kwargs):
        self._container = collections.OrderedDict()
        super(JSONDict, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        return self._container.__getitem__(key)
           
    def __getattr__(self, name):
        if name in self._protect_attributes:
            return super(JSONDict, self).__getitem__(name)
        return self.__getitem__(name)
                 
    @publish()
    def __setitem__(self, key, value):
        return self._container.__setitem__(key, value)
        
    def __setattr__(self, name, value):
        if name in self._protect_attributes:
            return super(JSONDict, self).__setattr__(name, value)
        if not is_JSONable(value):
            raise ValueError("Value must be jsonable.")
        self.__setitem__(name, value)

    @publish()
    def __delitem__(self, key):
        return self._container.__delitem__(key)
    
    def __delattr__(self, name):
        self.__delattr__(name)

    def __iter__(self):
        return self._container.__iter__()
        
    def __len__(self):
        return self._container.__len__()

    def __repr__(self):
        cls_name = self.__class__.__name__
        json_string = self.as_JSON()
        str = "{}.from_JSON({})".format(cls_name, json_string)
        return str

    def as_dict(self):
        return self._container

    def as_JSON(self):
        payload = json_encoder.encode(self)
        return payload

    def set_JSON(self, json_string):
        self._container = json.loads(json_string, object_pairs_hook=collections.OrderedDict)

    @classmethod
    def from_JSON(cls, json_string):
        instance = cls()
        instance.set_JSON(json_string)
        return instance
