"""This module contains the dictionary implimentations of
Publisher.

"""
import collections
import json
from autopubpy.models.basemodel import json_encoder
from autopubpy.pubsub import Publisher, method_publish


class SyncDict(Publisher, collections.MutableMapping):
    """Dictionary implementation of Publisher.

    This class can be used just like a dict and publishes changes 
    via the method_publish decorator

    attributes:
        data (iterable): The data that populates the dict.
        dict_factory(MutableSequence): The type of dict that is populated.    
        
    """
    dict_factory = dict

    def __init__(self, data=None, dict_factory=None, *args, **kwargs):
        if dict_factory is not None:
            self.dict_factory = dict_factory
        if data is None:
            self._container = self.dict_factory()
        else:
            self._container = self.dict_factory(data)
        super(SyncDict, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        return self._container.__getitem__(key)

    @method_publish()
    def __setitem__(self, key, value):
        return self._container.__setitem__(key, value)
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

    def as_json(self):
        payload = json_encoder.encode(self._container)
        return payload

    def set_json(self, json_string):
        container = json.loads(json_string)
        if not isinstance(container, self.dict_factory):
            container = self.dict_factory(container)
        self._container = container

    @classmethod
    def from_JSON(cls, json_string):
        instance = cls()
        instance.set_json(json_string)
        return instance


class SyncOrderedDict(SyncDict):
    """OrderedDict implimentation of Publisher.

    """
    dict_factory = collections.OrderedDict

    def set_json(self, json_string):
        container = json.loads(json_string, object_pairs_hook=collections.OrderedDict)
        if not isinstance(container, self.dict_factory):
            container = self.dict_factory(container)
        self._container = container

"""
class _SyncDictNameSpace(Publisher, collections.MutableMapping):
    _protect_attributes = ['_propagate', '_subscribers', '_topic_prefix', '_container']
    def __init__(self, *args, **kwargs):
        self._container = collections.OrderedDict()
        super(SyncDictNameSpace, self).__init__(*args, **kwargs)

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
            return super(SyncDictNameSpace, self).__setattr__(name, value)
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
"""