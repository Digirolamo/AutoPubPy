"""Class and functions for creating Publisher models.

This module contains the building blocks used to create
Publisher models. The models in models.py are created using
this module.

"""
import collections
import functools
import weakref
from autobahn import wamp
from autobahn.wamp.types import SubscribeOptions, PublishOptions
from twisted.internet.defer import inlineCallbacks, returnValue


class Publisher(object):
    """

    Subclass this object to create datatypes that publish method calls to
    various sessions.

    Attributes:
        topic (unicode): The base URI of publish events.

    
    """
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


def method_publish(topic=u"", options=PublishOptions()):
    """A function that returns a publishing decorator.

    When creating a Publisher subclass, use this function to decorate
    methods you intend to publish. When the method is called, both the 
    method name, and the arguments are published to the topic.

    Args:
        topic (unicode): The URI topic that the method will call on publish.
            This topic is appened to the Publishers .topic.
        options (PublishOptions): The publish options used with subscriber.publish

    Returns:
        callable: The function intended to decorate a method of a Publisher subclass.

    Examples:
        class DailyMessage(Publisher):
            topic = 'com.dailymessage'
            def __init__(self, message=None):
                super(DailyMessage, self).__init__()
                self._message = ""
                if message is not None:
                    self.set_message(message)

            @method_publish(topic="message_changed")
            def set_message(self, message):
                self._message = message

        daily_message = DailyMessage()
        daily_message.set_message("Hello World")

        #Explanation
        In this example, using set_message("Hello World") calls 
        session.publish(
            #The Topic
            "com.dailymessage.message_changed", 

            #The *args
            ("Hello World, ),
            
            #The **kwargs along with 'method' and 'options'
            {'method': 'set_message',
            'options': <PublishOptions> instance}
            )                      

    """
    if not isinstance(topic, unicode):
        raise TypeError("Topic must be unicode not {}.".format(type(topic)))
    if not isinstance(options, PublishOptions):
        raise TypeError("options must be PublishOptions not {}.".format(type(options)))
    def publish_decorator(func):
        if not isinstance(func, callable):
            raise TypeError("Decorator must be used on a Publisher method. "
                "Cannot be used on {}.".format(type(func)))
        @functools.wraps(func)
        def publish_after(self, *args, **kwargs):
            if not isinstance(self, Publisher):
                raise TypeError("method_publish must be used on a Publisher subclass. "
                    "Cannot be used on {}.".format(func.__name__))
            return_value = func(self, *args, **kwargs)
            print func.__name__
            kwargs['options'] = options
            kwargs['method'] = func.__name__
            #print self, len(self.subscribers), self.subscribers
            if self._propagate:
                if not topic:
                    pub_topic = self.topic
                else:
                    pub_topic = "{base}.{topic}".format(self.topic, topic)
                    print pub_topic, self, args, kwargs
                for subscriber in self.subscribers:
                    subscriber.publish(pub_topic, *args, **kwargs)
            return return_value
        return publish_after
    return publish_decorator