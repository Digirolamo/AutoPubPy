"""This module contains an application class that emits Qt Signals."""
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from PySide import QtCore
from twisted.internet.defer import inlineCallbacks

class State(object):
    """The state of a websocket connection."""
    DISCONNECTED = 0
    WAITING = 1
    CONNECTED = 2

class _QUserSessionSignals(QtCore.QObject):
    """Used for wrapping signal. Hard to mix in Twisted
    and Qt classes because they share method names. This is a wrapper."""
    SessionOpened = QtCore.Signal(object, object)
    SessionConnect = QtCore.Signal(object, object)
    SessionDisconnectd = QtCore.Signal(object, object)   
    SessionJoined = QtCore.Signal(object, object)
    SessionLeft = QtCore.Signal(object, object)

class QApplicationSession(ApplicationSession):
    """{description here}

    Attributes:
        SessionConnect (QtCore.Signal): Emited when onConnect is called.
        SessionDisconnected (QtCore.Signal): Emited when onDisconnect is called.
    """
    last_connection = None

    def __init__(self, *args, **kwargs):
        if self.last_connection is not None:
            raise ValueError("Can't have more than one connection at this time.")
        self._q_object = _QUserSessionSignals()
        self.SessionOpened = self._q_object.SessionOpened
        self.SessionConnect = self._q_object.SessionConnect
        self.SessionDisconnectd = self._q_object.SessionDisconnectd
        self.SessionJoined = self._q_object.SessionJoined
        self.SessionLeft = self._q_object.SessionLeft
        super(QApplicationSession, self).__init__(*args, **kwargs)
        QUserSession.last_connection = self

    def onOpen(self, transport):
        """
        Callback fired when transport is open.

        A WAMP transport is a bidirectional, full-duplex, reliable, ordered, message-based channel.

        Args:
            transport (autobahn.wamp.interfaces.ITransport) - instance that implements ITransport
            """
        super(QApplicationSession, self).onConnect(transport)
        self.SessionOpened.emit(self, transport)

    def onConnect(self):
        """
        Callback fired when the transport this session will run over has been established.
        """
        super(QApplicationSession, self).onConnect()
        self.SessionConnect.emit(self, State.CONNECTED)

    
    def onChallenge(self, challenge):
        """
        Callback fired when the peer demands authentication.
        May return a Deferred/Future.

        Args:
            challenge (autobahn.wamp.types.Challenge.) - The authentication challenge.
        """

    def onJoin(self, details):
        """
        Callback fired when WAMP session has been established.
        May return a Deferred/Future.

        Args:
            details (autobahn.wamp.types.SessionDetails.) - Session information.
        """
        super(QApplicationSession, self).onJoin(details)
        self.SessionJoined.emit(self, details)

    def onLeave(self, details):
        """
        Callback fired when WAMP session has is closed

        Args:
            details (autobahn.wamp.types.CloseDetails.) - Close information.
        """
        super(QApplicationSession, self).onLeave(details)
        self.SessionLeft.emit(self, details)

    def onDisconnect(self):
        """
        Callback fired when underlying transport has been closed.
        """

        super(QApplicationSession, self).onDisconnect()
        self.SessionDisconnectd.emit(self, State.DISCONNECTED)

    def user_publish(self, topic, data):
        """Publishes data to the user uri space of the realm..
        
        Appends 'com' and the username to the uri topic.

        Args:
            topic (unicode): The topic to be published.
                Will be the end of the uri.
            data (object): Data that can be published.
        
        """
        uri = u"com.{username}.{topic}".format(
            username=self._userid, topic=topic)
        self.publish(uri, data)

    

    #def publish(self, topic, *args, **kwargs):
    #    """
    #    """

    #def subscribe(self, handler, topic=None, options=None):
    #    """
    #    """

    #def call(self, procedure, *args, **kwargs):
    #    """
    #    """

    #def register(self, endpoint, procedure=None, options=None):
    #    """
    #    """


