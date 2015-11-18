"""This module contains some helpful ssl and tls functions.
"""
from OpenSSL import SSL
from twisted.internet import ssl


class TLSClientContextFactory(ssl.ClientContextFactory):  #pylint: disable=no-init, too-few-public-methods
    """Subclassed to prefer TLS and avoid using SSL."""

    method = SSL.TLSv1_2_METHOD

    def getContext(self):
        ctx = self._contextFactory(self.method)
        ctx.set_options(SSL.OP_NO_SSLv2 | SSL.OP_NO_SSLv3)
        return ctx


def get_protocol_name(deferedwamp):
    """Gets the protocol name the session. is using.

    Args:
        deferedwamp (): The

    """
    conn = deferedwamp.result.transport.getHandle()
    from OpenSSL._util import ffi, lib
    #use to be lib.SSL_get_version
    version = ffi.string(lib.SSL_CIPHER_get_version(conn._ssl))  #pylint: disable=protected-access, no-member
    return version.decode("utf-8"), conn.get_cipher_name()
