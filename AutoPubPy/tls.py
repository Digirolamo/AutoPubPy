from OpenSSL import SSL
from twisted.internet import ssl

class TLSClientContextFactory(ssl.ClientContextFactory):
    """Avoid using ssl."""
    method = SSL.TLSv1_2_METHOD
    def getContext(self):
        ctx = self._contextFactory(self.method)
        ctx.set_options(SSL.OP_NO_SSLv2 | SSL.OP_NO_SSLv3)
        return ctx

def get_protocol_name(deferedwamp):
    conn = deferedwamp.result.transport.getHandle()
    from OpenSSL._util import ffi, lib 
    version = ffi.string(lib.SSL_get_version(conn._ssl))
    return version.decode("utf-8"), conn.get_cipher_name()