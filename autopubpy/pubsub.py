"""Class and functions for creating Publisher models.

This module contains the building blocks used to create
Publisher models. The models in models.py are created using
this module.

"""
import contextlib
import functools
import types
import weakref
from autobahn.wamp.exception import TransportLost
from autobahn.wamp.types import PublishOptions
from twisted.internet.defer import inlineCallbacks, returnValue


class Publisher(object):
    """

    Subclass this object to create datatypes that publish method calls to
    various sessions.

    Attributes:
        topic (unicode): The base URI of publish events.
        update_method (unicode): The name of the method you use to set
            the state of an instance. Default is as_json.

    """
    topic = 'com'
    update_method = "as_json"

    def __init__(self):
        self._propagate = True
        self._topic_prefix = u"com.myapp.{}".format(unicode(id(self)))
        self._subscribers = weakref.WeakSet()

    @property
    def subscribers(self):
        """generator(session): Returns a generator of the
        subscribed sessions.

        """
        return (session for session in self._subscribers)

    def subscribe(self, session):
        """Add a session to the subscriber set.

        Note:
            Only a weak reference to the session will be stored.

        Args:
            session (ApplicationSession): The subscribing session.

        """
        self._subscribers.add(session)

    def unsubscribe(self, subscriber):
        """Remove a session from the subscriber set.

        Args:
            session (ApplicationSession): The subscribing session to remove.

        """
        if subscriber not in self._subscribers:
            raise KeyError("Must be subscribed to unsubscribe. "
                           "Object {} is not subscribed.".format(type(subscriber)))
        self._subscribers.remove(subscriber)

    @contextlib.contextmanager
    def block_propagation(self):
        """
        Context manager that prevents sync events from being
        sent out by methods decorated with method_publish.

        Example:
            with synclist.block_propogation:
                synclist.clear()
        
        """
        self._propagate = False
        yield
        self._propagate = True

    def _receive_sync_event(self, *args, **kwargs):
        """When published events are propagated from a synced instance
        in another session this method is called and we call
        the same method on this instance.

        """
        if 'method' not in kwargs:
            raise KeyError("kwargs must have 'method' key.")
        method_name = kwargs['method']
        method = getattr(self, method_name)
        with self.block_propagation():
            return method(*args)

    def as_json(self, json_string):
        """Reimpliment this method to get the state of the object."""
        raise NotImplementedError("You must impliment as_json in a subclass.")

    def set_json(self, json_string):
        """Reimpliment this method to set the state of the object."""
        raise NotImplementedError("You must impliment set_json in a subclass.")

    @inlineCallbacks
    def set_main_session(self, session):
        """Sets the main session of the Sync list, basically
        the mothership server."""
        cls = self.__class__
        topic = cls.topic
        instance = self
        yield instance.subscribe(session)
        get_state_topic = topic + "." + cls.update_method
        print 'uri', get_state_topic
        yield session.register(getattr(instance, cls.update_method), get_state_topic)
        yield session.subscribe(instance._receive_sync_event, topic)  #pylint: disable=protected-access
        returnValue(instance)

    @classmethod
    @inlineCallbacks
    def create_new(cls, session, topic=None):
        """Creates a new Publisher instance to be used with the session.

        Args:
            session (ApplicationSession): The subscribing session to remove.
            topic (unicode): The base URI of publish events.
                If topic is None, use the cls.topic string.

        """
        if topic is None:
            topic = cls.topic
        instance = cls()
        yield instance.subscribe(session)
        get_state_topic = topic + "." + cls.update_method
        print 'uri', get_state_topic
        yield session.register(getattr(instance, cls.update_method), get_state_topic)
        yield session.subscribe(instance._receive_sync_event, topic)  #pylint: disable=protected-access
        returnValue(instance)

    @classmethod
    @inlineCallbacks
    def create_from_server(cls, session, topic=None):
        """Creates a Publisher instance from another session and
        sets the initial state to match.

        Args:
            session (ApplicationSession): The subscribing session to remove.
            topic (unicode): The base URI of publish events.
                If topic is None, use the cls.topic string.

        """
        if topic is None:
            topic = cls.topic
        instance = cls()
        yield session.subscribe(instance._receive_sync_event, topic)  #pylint: disable=protected-access
        original_state_topic = topic + "." + cls.update_method
        json_string = yield session.call(original_state_topic)
        instance.set_json(json_string)
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

            @method_publish(topic="message_changed")
            def set_message(self, message):
                self._message = message

        daily_message = DailyMessage()
        daily_message.set_message("Hello World")

        #Explanation
        In this example, using set_message("Hello World") calls
        session.publish(

            #The full URI
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
        """Decorates a Publisher method. When the method is called
        publishes an event. See method_publish.

        Args:
            func (FunctionType): The method to be decorated.

        """
        if not isinstance(func, types.FunctionType):
            raise TypeError("Decorator must be used on a Publisher method. "
                            "Cannot be used on {}.".format(type(func)))
        @functools.wraps(func)
        def publish_after(self, *args, **kwargs):  #pylint: disable=missing-docstring
            if not isinstance(self, Publisher):
                raise TypeError("method_publish must be used on a Publisher subclass. "
                                "Cannot be used on {}.".format(func.__name__))
            return_value = func(self, *args, **kwargs)
            print func.__name__
            kwargs['options'] = options
            kwargs['method'] = func.__name__
            #print self, len(self.subscribers), self.subscribers
            if self._propagate:  #pylint: disable=protected-access
                if not topic:
                    pub_topic = self.topic
                else:
                    pub_topic = "{base}.{topic}".format(base=self.topic, topic=topic)
                    print pub_topic, self, args, kwargs
                for subscriber in self.subscribers:
                    try:
                        subscriber.publish(pub_topic, *args, **kwargs)
                    except TransportLost as e:
                        print e
                    except Exception as e:
                        print e
            return return_value
        return publish_after
    return publish_decorator
