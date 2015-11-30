"""This module contains component classes for server and client
authorization and authentication.

Note:
    These are different things.
        Authentication determines who the client is and whether or not
            you allow the login.

        Authorization determines what permissions the connected
            client has. Both in terms of URI's and methods (pub, sub, call, reg).

"""
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError


class AuthComponent(ApplicationSession):
    """A server component intented to subclass for authenticating and
    authorizing clients and actions.

    Note:
        Authenticating and Authorizing are different things.
        Authentication determines who the client is and whether or not
            you allow the login.

        Authorization determines what permissions the connected
            client has. Both in terms of URI's and methods (pub, sub, call, reg).

    """

    def authenticator(self, realm, authid, ticket):  #intended ot be overwridden pylint: disable=unused-argument,no-self-use
        """Authenticates a user and returns the user role.

           This function attempts to authenticate a user using
           ticket authentication.

        Args:
            realm (unicode): The realm the client is attempting to
                connect to.
            authid (unicode): The identification of the client. The client
                provides this information.
            ticket (unicode): The password/ticket the client responses via their
                onChallenge method.

        Returns:
            unicode: The role of the user.

        Raises:
            ApplicationError: If the user is not authenticated successfully this
                exception is raised.

        """
        raise ApplicationError("authenticator needs to be implimented!")

    def authorizer(self, session, uri, action):  #intended ot be overwridden pylint: disable=unused-argument,no-self-use
        """Determines whether or not to allow the requested action.

        Args:
            session (dict): A dictionary of the session details, example:
                {"realm": "realm1",
                "authprovider": None,
                "authid": "VA-TKRAaIT44meQKZ6n5y7wk",
                "authrole": "frontend",
                "authmethod": "anonymous",
                "session": 1849286409148650}
            uri (unicode): The URI of the requested action.

        Returns:
            bool: True if the action should be allowed, False otherwise.

        """
        try:
            authid = session['authid']
            print "authorize called", authid, action, uri
            raise NotImplementedError
            #return True
        except Exception:  #False prevents logins pylint: disable=broad-except
            return False


    @inlineCallbacks
    def onJoin(self, details):
        try:
            yield self.register(self.authenticator, 'com.authenticate')
            yield self.register(self.authorizer, 'com.authorize')
        except Exception:  #log problem pylint: disable=broad-except
            print ("Could not register AuthComponent's "
                   "authenticator and authorizer fucntions.")


class ClientAuthComponent(ApplicationSession):
    """A client component intented to be used as-is or subclassed for
    responding to authenticating.

    """

    @classmethod
    def set_default_user_id(cls, userid):
        """Sets the default userid (authid) of the component class.

        Args:
            userid (unicode): The authid unique identifier of the client.
                Could be a username.

        """
        if not isinstance(userid, unicode):
            raise ValueError("userid must be unicode, not {}."
                             "".format(type(userid)))
        cls._userid = userid

    @classmethod
    def set_default_password(cls, password):
        """Sets the default password of the component class.

        Args:
            password (unicode): The password or secret key for the client.
        """
        if not isinstance(password, unicode):
            raise ValueError("password must be unicode, not {}."
                             "".format(type(password)))
        cls._password = password

    def onConnect(self):
        """Connects using the set username."""
        if (not isinstance(self._userid, unicode) or
                not isinstance(self._password, unicode)):
            raise ValueError("authid and password must both be unicode, not "
                             "{} and {}"
                             "".format(type(self._userid), type(self._password)))
        username = self._userid
        realm = self.config.realm
        auth_type = [u"ticket"]
        self.join(realm, auth_type, username)

    def onChallenge(self, challenge):
        """Responds to the challenge with the password.

        Args:
            challenge (Challenge): Contains attributes method and
                extra.
        """
        #print challenge.extra, challenge.extra
        if challenge.method == u"ticket":
            signature = 'test'.decode('ascii')
            return signature
        else:
            raise ValueError("Can only respond to ticket, not "
                             "{}".format(challenge.method))
