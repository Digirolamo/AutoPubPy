import collections
import weakref
from functools import wraps

from autobahn import wamp
from autobahn.wamp.types import SubscribeOptions, PublishOptions
from twisted.internet.defer import inlineCallbacks, returnValue

def publish(topic=None, options=PublishOptions()):  
    def publish_decorator(func):
        @wraps(func)
        def publish_after(self, *args, **kwargs):
            return_value = func(self, *args, **kwargs)
            print func.__name__
            pub_id = unicode(id(self))
            #pub_topic = u"{}.{}.{}".format(topic, pub_id)
            kwargs['options'] = options
            kwargs['method'] = func.__name__
            #print self, len(self.subscribers), self.subscribers
            if self._propagate:
                for subscriber in self.subscribers:
                    pub_topic = self.topic
                    print pub_topic, self, args, kwargs
                    subscriber.publish(pub_topic, *args, **kwargs)
            return return_value
        return publish_after
    return publish_decorator

class Publisher(object):
    "publisher doc"
    topic = 'com'
    update_method = "as_JSON"
    def __init__(self):
        self._propagate = True
        self._topic_prefix = u"com.myapp.{}".format(unicode(id(self)))
        self._subscribers = weakref.WeakSet()
        
    @property
    def subscribers(self):
        return self._subscribers
    
    def subscribe(self, subscriber):
        self._subscribers.add(subscriber)
        
    def unsubscribe(self, subscriber):
        if subscriber not in self._subscribers:
            raise KeyError("Must be subscribed to unsubscribe. "
                "Object {} is not subscribed.".format(type(subscriber)))
        self._subscribers.remove(subscriber)
    
    def on_sync_event(self, *args, **kwargs):
        if 'method' not in kwargs:
            raise KeyError("kwargs must have 'method' key.")
        method_name = kwargs['method']
        method = getattr(self, method_name)
        try:
            self._propagate = False
            return method(*args)
        finally:
            self._propagate = True
             

    @classmethod
    @inlineCallbacks
    def create_for_server(cls, session, topic=None):
        if topic is None:
            topic = cls.topic
        instance = cls()
        yield instance.subscribe(session)
        get_state_topic = topic + "." + cls.update_method
        print 'uri', get_state_topic
        yield session.register(getattr(instance, cls.update_method), get_state_topic)
        yield session.subscribe(instance.on_sync_event, topic)
        returnValue(instance)

    @classmethod
    @inlineCallbacks
    def create_from_server(cls, session, topic=None):
        if topic is None:
            topic = cls.topic
        instance = cls()
        yield session.subscribe(instance.on_sync_event, topic)
        original_state_topic = topic + "." + cls.update_method
        json_string = yield session.call(original_state_topic)
        instance.set_JSON(json_string)
        yield instance.subscribe(session)
        returnValue(instance)
