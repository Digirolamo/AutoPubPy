from abc import ABCMeta, abstractmethod
import collections
import copy
import json
from autopubpy.pubsub import Publisher, method_publish

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
    def as_json(self):
        """Returns the object in it's json form."""

class JSONable(object):
    __metaclass__ = MetaJSON


class SyncDict(Publisher, collections.MutableMapping):
    """An OrderedDict that can be synced across machines"""
    topic = 'com.dict'
    _protect_attributes = ['_propagate', '_subscribers', '_topic_prefix', '_container']
    def __init__(self, *args, **kwargs):
        self._container = collections.OrderedDict()
        super(SyncDict, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        return self._container.__getitem__(key)

    def __getattr__(self, name):
        if name in self._protect_attributes:
            return super(SyncDict, self).__getitem__(name)
        return self.__getitem__(name)

    @method_publish()
    def __setitem__(self, key, value):
        return self._container.__setitem__(key, value)

    def __setattr__(self, name, value):
        if name in self._protect_attributes:
            return super(SyncDict, self).__setattr__(name, value)
        if not is_JSONable(value):
            raise ValueError("Value must be jsonable.")
        self.__setitem__(name, value)

    @method_publish()
    def __delitem__(self, key):
        return self._container.__delitem__(key)

    def __delattr__(self, name):
        self.__delattr__(name)

    def __iter__(self):
        return self._container.__iter__()

    def __len__(self):
        return self._container.__len__()

    def __repr__(self):
        return self._container.__repr__()

    def as_dict(self):
        return self._container

    def as_json(self):
        payload = json_encoder.encode(self._container)
        return payload

    def set_json(self, json_string):
        self._container = json.loads(json_string, object_pairs_hook=collections.OrderedDict)

    @classmethod
    def from_JSON(cls, json_string):
        instance = cls()
        instance.set_json(json_string)
        return instance

class SyncList(Publisher, collections.MutableSequence):
    """A class that can be used just like a list and publishes changes via the method_publish decorator

    attributes:
        container (list): The list object that is synced across machines
        auto_publish (bool): if true changing the list will publish the list
    """
    list_factory = list
    def __init__(self, data=None, *args, **kwargs):
        if data is None:
            self._container = self.list_factory()
        else:
            self._container = self.list_factory(start)
        super(SyncList, self).__init__(*args, **kwargs)
        
    def __getitem__(self, key):
        return self._container.__getitem__(key)

    @method_publish()
    def __setitem__(self, key, value):
        return self._container.__setitem__(key, value)

    @method_publish()
    def __delitem__(self, key):
        return self._container.__delitem__(key)
        
    def __len__(self):
        return len(self._container)
    
    def __repr__(self):
        return repr(self._container)
    
    def __str__(self):
        return str(self._container)
    
    @method_publish()
    def insert(self, indx, v):
        rtn = self._container.insert(indx, v)
        return rtn
    
    @method_publish()
    def sort(self, *args, **kwargs):
        self._container.sort(*args, **kwargs)
        
    def as_json(self):
        payload = json_encoder.encode(self._container)
        return payload

    def set_json(self, json_string):
        """Reimpliment this method to set the state of the object."""
        self._container = self.list_factory(json.loads(json_string))
