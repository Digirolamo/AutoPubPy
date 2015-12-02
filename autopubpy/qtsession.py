"""This module contains an application class that emits Qt Signals."""
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from PySide import QtCore
from twisted.internet.defer import inlineCallbacks

class _QUserSessionSignals(QtCore.QObject):
    """Used for wrapping signal. Hard to mixin Twisted
    and Qt classes because they share method names. This is a wrapper."""
    SessionOpened = QtCore.Signal(object, object)
    SessionConnected = QtCore.Signal(object)


class QApplicationSession(ApplicationSession):
    """{description here}

    Args:
        SessionConnected (QtCore.Signal): Emited when onConnect is
            called.

    """

    def __init__(self, *args, **kwargs):
        self._q_object = _QUserSessionSignals()
        self.SessionOpened = self._q_object.SessionOpened
        self.SessionConnected = self._q_object.SessionConnected
        super(QApplicationSession, self).__init__(*args, **kwargs)

    def onOpen(self, transport):
        """{description here}

        Args:
            transport ({type here}): blah

        """
        super(QApplicationSession, self).onConnect(transport)
        self._q_object.SessionOpened.emit(self, transport)

    def onConnect(self):
        """{description here}

        """
        super(QApplicationSession, self).onConnect()
        self._q_object.SessionConnected.emit(self)
