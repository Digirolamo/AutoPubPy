from autopubpy.pubsub import Publisher, method_publish
from autopubpy.models import json_encoder
import json
from autobahn.twisted.wamp import ApplicationSession


import collections
class SyncList(Publisher, collections.MutableSequence):
    def __init__(self, start=[], *args, **kwargs):
        self._container = list(start)
        self._auto_publish = True
        super(SyncList, self).__init__(*args, **kwargs)
        
    def __getitem__(self, key):
        return self._container.__getitem__(key)
        
    def __setitem__(self, key, value):
        if not self._auto_publish:
            return self._container.__setitem__(key, value)
        else:
            self._setitem_publish(key, value)

    @method_publish
    def _setitem_publish(self, key, value):
        return self._container.__setitem__(key, value)
        
    def __delitem__(self, key):
        if not self._auto_publish:
            return self._container.__delitem__(key)
        else:
            self._delitem_publish(key)

    @method_publish
    def _delitem_publish(self, key):
        return self._container.__delitem__(key)
        
    def __len__(self):
        return len(self._container)
    
    def __repr__(self):
        return repr(self._container)
    
    def __str__(self):
        return str(self._container)
    
    def insert(self, indx, v):
        return self._container.insert(indx, v)
    
    def sort(self, *args, **kwargs):
        self._container.sort(*args, **kwargs)
        if self._auto_publish:
            self.sync()
        
    def as_json(self):
        payload = json_encoder.encode(self._container)
        return payload

    def set_json(self, json_string):
        """Reimpliment this method to set the state of the object."""
        self._container = json.loads(json_string)

    
    def sync(self):
        """Publishes the contents of the list to all current subscribers"""
        self._sync_helper(self._container)
        
    @method_publish()
    def _sync_helper(self, item):
        item = list(item)
        self._container = item[:]

    def set_auto_publish(self, v):
        """set this object to publish any changes to it automatically.

        args:
            v (bool): the mode auto publish
        """
        self._auto_publish = v



"""
class TestSession(ApplicationSession):

    def onJoin(self):
        self.syncing_string = SyncString.create_new(self)
        self.syncing_string.set_string('blah')


class TestSession2(ApplicationSession):

    def onJoin(self):
        self.syncing_string = SyncString.create_from_server(self)


class TestSession3(ApplicationSession):

    def onJoin(self):
        self.syncing_string = SyncString.create_from_server(self)
        self.syncing_string.set_string('kyle')
"""