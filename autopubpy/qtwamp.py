"""This module contains classes that mixin wamp and qt classes.
The classes emit Qt Signals along with calling the usual twisted
methods.

"""
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.exception import ApplicationError
from PySide import QtCore
from twisted.internet.defer import inlineCallbacks


class _QApplicationRunnerSignals(QtCore.QObject):
    """Used for wrapping signal. Hard to mix in Twisted
    and Qt classes because they share method names. This is a wrapper."""
    CreatedSession = QtCore.Signal(object)
    FailedCreatingSession = QtCore.Signal(object, object)


class QApplicationRunner(ApplicationRunner):
    """Allows Qt signals to be emitted with Autobahn ApplicationRunner.

    Class Signals (QtCore.Signal):
        CreatedSession (): Emitted when session instance is created.
        FailedCreatingSession (): Emitted when there is an
            error creating a session.

    """
    def __init__(self, *args, **kwargs):
        self._q_object = _QApplicationRunnerSignals()
        self.CreatedSession = self._q_object.CreatedSession
        self.FailedCreatingSession = self._q_object.FailedCreatingSession
        super(QApplicationRunner, self).__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        """Override run to hook failure and success methods."""
        defered = super(QApplicationRunner, self).run(*args, **kwargs)
        defered.addErrback(self.failed_to_create_session)
        defered.addCallback(self.created_session)
        return defered

    def created_session(self, *args):
        """If we create the session, emit a signal."""
        self._q_object.CreatedSession.emit()

    def failed_to_create_session(self, *args):
        """If we never create the session, emit a signal."""
        self._q_object.FailedCreatingSession.emit()

class _QApplicationSessionClassSignals(QtCore.QObject):
    """Used for wrapping signal. Hard to mix in Twisted
    and Qt classes because they share method names. This is a wrapper."""
    SessionCreated = QtCore.Signal(object)


class _QApplicationSessionSignals(QtCore.QObject):
    """Used for wrapping signal. Hard to mix in Twisted
    and Qt classes because they share method names. This is a wrapper."""
    SessionOpened = QtCore.Signal(object, object)
    SessionConnected = QtCore.Signal(object)
    SessionJoined = QtCore.Signal(object, object)
    SessionLeft = QtCore.Signal(object, object)
    SessionDisconnected = QtCore.Signal(object, object)


class QApplicationSession(ApplicationSession):
    """
    Allows Qt signals to be emitted with Autobahn ApplicationSession method calls, the problem with#
    having this inherit from QObject is the two classes have methods with the same name making it 
    messy trying to mix the two

    At least for ipython, it won't create a session if this as an __ini__ method


    Class Signals (QtCore.Signal):
        SessionCreated (QtCore.Signal): Emitted when session instance is created.

    Instance Signals (QtCore.Signal):
        SessionOpened (QtCore.Signal): Emitted when a transport is opened.
        SessionConnected (QtCore.Signal): Emitted when onConnect is called.
        SessionJoined (QtCore.Signal): Emitted when onJoin is called.  WAMP session is established
        SessionLeft (QtCore.Signal): Emitted when onLeave is called. WAMP session is closed
        SessionDisconnected (QtCore.Signal): Emitted when onDisconnect is called.      

    """
    _class_q_object = _QApplicationSessionClassSignals()
    SessionCreated = _class_q_object.SessionCreated
    last_session = None

    def __init__(self, *args, **kwargs):
        QApplicationSession.last_session = last_session
        self._q_object = _QApplicationSessionSignals()
        self.SessionOpened = self._q_object.SessionOpened
        self.SessionConnected = self._q_object.SessionConnected
        self.SessionDisconnected = self._q_object.SessionDisconnected
        self.SessionJoined = self._q_object.SessionJoined
        self.SessionLeft = self._q_object.SessionLeft
        super(QApplicationSession, self).__init__(*args, **kwargs)
        QApplicationSession.SessionCreated.emit(self)
        
    def onOpen(self, transport):
        """
        Callback fired when transport is open.

        Args:
            transport (WampWebSocketClientProtocol) - WampWebSocketClientProtocol is the base class 
                for Twisted-based WAMP-over-WebSocket client protocols.

        """
        super(QApplicationSession, self).onOpen(transport)
        self.SessionOpened.emit(self, self.SessionOpened)
    
    def onConnect(self):
        """
        Callback fired when the transport this session will run over has been established.
        """
        super(QApplicationSession, self).onConnect()
        self.SessionConnected.emit(self)
        
    def onJoin(self, details):
        """
        Callback fired when WAMP session has been established.

        May return a Deferred/Future.

        Args:
            details (autobahn.wamp.types.SessionDetails) - Provides details for a WAMP session upon open.
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
        self.SessionDisconnected.emit(self)
