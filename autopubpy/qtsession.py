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
    """
    Allows Qt signals to be emitted with Autobahn ApplicationSession method calls, the problem with
    having this inherit from QObject is the two classes have methods with the same name making it 
    messy trying to mix the two

    At least for ipython, it won't create a session if this as an __ini__ method

    Attributes:
        SessionOpened (QtCore.Signal): Emitted when a transport is opened?
        SessionConnect (QtCore.Signal): Emitted when onConnect is called.
        SessionJoined (QtCore.Signal): Emitted when onJoin is called.  WAMP session is established
        SessionLeft (QtCore.Signal): Emitted when onLeave is called. WAMP session is closed
        SessionDisconnected (QtCore.Signal): Emitted when onDisconnect is called.      
    """
    last_session = None

    def __init__(self, *args, **kwargs):
        self._q_object = _QUserSessionSignals()
        self.SessionOpened = self._q_object.SessionOpened
        self.SessionConnect = self._q_object.SessionConnect
        self.SessionDisconnectd = self._q_object.SessionDisconnectd
        self.SessionJoined = self._q_object.SessionJoined
        self.SessionLeft = self._q_object.SessionLeft
        super(QApplicationSession, self).__init__(*args, **kwargs)

        
    def onOpen(self, transport):
        super(QApplicationSession, self).onOpen(transport)
        self.SessionOpened.emit(self, transport)
    
    def onConnect(self):
        """
        Callback fired when the transport this session will run over has been established.
        """
        super(QApplicationSession, self).onConnect()
        self.SessionConnect.emit(self, State.CONNECTED)
        
    def onJoin(self, details):
        QApplicationSession.last_session = self
        super(QApplicationSession, self).onJoin(details)
        
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