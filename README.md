AutoPubPy
=======

Convenient models and more for sharing data structures using Autobahn-Python (WebSocket / WAMP).

**Warning:** A private version of AutoPubPy is maintained and tested. This public version isn't as complete and caution should be used until it is more robust.

Idea
------------
 - Share python data structures across multiple python sessions using websockets.
 - Convenient base models to create more advanced models.

Here is a simple example:
(`session` is an already created autobahn/twisted `ApplicationSession` for each session, the pub/sub/rpc authority is determined by the crossbar server)

    Main Session
    >>> from autopubpy.models import SyncList
    >>> color_list = SyncList(name='colors')
    >>> color_list.set_client_session(session)
    >>>
    >>> color_list.append('red')
    ['red']
    
    Other Session/s
    >>> from autopubpy.models import SyncList
    >>> color_list = SyncList(name='colors')
    >>> color_list.set_client_session(session)
    >>> color_list
    ['red']
    
    Main Session
    >>> color_list.pop()
    
    >>> # Other Session/s
    >>> color_list
    []
    

Requirements
------------
- [twisted](https://pypi.python.org/pypi/Twisted)
- [autobahn](http://autobahn.ws/python/installation.html)
Install
------------
Currently the source code is hosted at:
https://github.com/Digirolamo/AutoPubPy
There will be a PyPi release only if the package grows.
