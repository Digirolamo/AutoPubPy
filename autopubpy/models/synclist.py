"""This module contains the list implimentation of
Publisher.

"""
import collections
import json
from autopubpy.models.basemodel import json_encoder
from autopubpy.pubsub import Publisher, method_publish


class SyncList(Publisher, collections.MutableSequence):
    """MutableSequence implementation of Publisher.

    This class can be used just like a list and publishes changes 
    via the method_publish decorator

    attributes:
        data (iterable): The data that populates the list.
        list_factory(MutableSequence): The type of list that is populated.

    """
    list_factory = list

    def __init__(self, data=None, list_factory=None, *args, **kwargs):
        if list_factory is not None:
            self.list_factory = list_factory
        if data is None:
            self._container = self.list_factory()
        else:
            self._container = self.list_factory(data)
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
    
    def __unicode__(self):
        return unicode(self._container)
    
    @method_publish()
    def insert(self, index, value):
        return_value = self._container.insert(index, value)
        return return_value
    
    @method_publish()
    def sort(self, *args, **kwargs):
        self._container.sort(*args, **kwargs)
        
    def as_json(self):
        """Returns the entire json string of the container."""
        payload = json_encoder.encode(self._container)
        return payload

    def set_json(self, json_string):
        container = json.loads(json_string)
        if not isinstance(container, self.list_factory):
            container = self.list_factory(container)
        self._container = container
