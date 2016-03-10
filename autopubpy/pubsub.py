"""Class and functions for creating Publisher models.

This module contains the building blocks used to create
Publisher models. The models in models.py are created using
this module.

"""
import abc
import contextlib
import functools
import types
import weakref
from autobahn.wamp.exception import TransportLost
from autobahn.wamp.types import PublishOptions
from twisted.internet.defer import inlineCallbacks, returnValue


class Publisher(object):
    """Abstract class of a publishing data structure.

    Subclass this object to create datatypes that publish method calls to
    various sessions. Impliment the abstract methods, and use the 
    "method_publish" decorator on methods that set the state of the object.

    Attributes:
        
        name (unicode): The name of the object, it will be appened at the end of the URI
            for publishing events.
        
    """
    __metaclass__ = abc.ABCMeta
    base_uri = None

    def __init__(self, base_uri='com', name=u""):
        self._connected = False
        self._object_name = name
        self._propagate = True
        self._subscribers = weakref.WeakSet()
        self.set_base_uri(base_uri)

    @abc.abstractmethod
    def as_json(self):
        """Reimpliment this method to get the state of the object.
        
        Example:
            def as_json(self):
                payload = json_encoder.encode(self._container)
                return payload

        Returns:
            unicode: The json representation of the object
        """
        raise NotImplementedError("You must impliment as_json in a subclass.")

    @abc.abstractmethod
    def set_json(self, json_string):
        """Reimpliment this method to set the state of the object.
        
        Args:
            json_string (unicode): The JSON state of the object, the format should
                match the as_json implimentation.

        Example:
            def set_json(self, json_string):
                self._container = json.loads(json_string, object_pairs_hook=collections.OrderedDict)

        """
        raise NotImplementedError("You must impliment set_json in a subclass.")

    @property
    def uri(self):
        """unicode: The base uri of this object.

        """
        return self._uri

    @property
    def subscribers(self):
        """generator(session): Returns a generator of the
        subscribed sessions.

        """
        return (session for session in self._subscribers)

    def set_base_uri(self, base_uri):
        """Sets the uri for events of this class.

        Args:
            base_uri (unicode): The base URI of publish events.

        Raises:
            ValueError: If already connected and a new base is set.

        """
        if self.base_uri == base_uri:
            return
        if self._connected:
            raise ValueError("Cannot change uri after object is connected.")
        self.base_uri = base_uri
        self._uri = base_uri
        if self._object_name:
            if self._uri:
                self._uri += u'.'
            self._uri += self._object_name

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

    def broadcast_sync(self):
        """Publishes a entire sync event to all current subscribers."""
        @method_publish()
        def set_json(self, json_string):
            pass
        set_json(self, self.as_json())
        
    @inlineCallbacks
    def set_main_session(self, session):
        """Sets the main session of the Sync list, basically
        the mothership server.
        
        Args:
            session (ApplicationSession): The twisted session connected
                to the router.
        
        """
        yield self.subscribe(session)
        update_method_name = self.as_json.__name__
        get_state_topic = self.uri + "." + update_method_name
        yield session.register(getattr(self, update_method_name), get_state_topic)
        yield session.subscribe(self._receive_sync_event, self.uri)  #pylint: disable=protected-access
        self.broadcast_sync()
        self._connected = True  #pylint: disable=protected-access
        returnValue(self)

    @inlineCallbacks
    def set_client_session(self, session):
        """Sets a client session of the data stcuture.
        
        Args:
            session (ApplicationSession): The twisted session connected
                to the router.
        
        """

        yield session.subscribe(self._receive_sync_event, self.uri)  #pylint: disable=protected-access
        update_method_name = self.as_json.__name__
        original_state_topic = self.uri + "." + update_method_name
        json_string = yield session.call(original_state_topic)
        self.set_json(json_string)
        yield self.subscribe(session)
        self._connected = True  #pylint: disable=protected-access
        returnValue(self)


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
            #print func.__name__
            kwargs['options'] = options
            kwargs['method'] = func.__name__
            #print self, len(self.subscribers), self.subscribers
            if self._propagate:  #pylint: disable=protected-access
                if not topic:
                    pub_topic = self.uri
                else:
                    pub_topic = "{base}.{topic}".format(base=self.uri, topic=topic)
                    print pub_topic, self, args, kwargs
                for subscriber in self.subscribers:
                    try:
                        subscriber.publish(pub_topic, *args, **kwargs)
                        print "Pub topic", pub_topic
                    except TransportLost as e:
                        print e
                    except Exception as e:
                        print e
            return return_value
        return publish_after
    return publish_decorator
