from autopubpy.pubsub import Publisher, method_publish
from autopubpy.models import json_encoder
import json
from autobahn.twisted.wamp import ApplicationSession


import collections



"""
class TestSession(ApplicationSession):

    def onJoin(self):
        self.syncing_string = SyncString.create_new(self)
        self.syncing_string.set_string('blah')


class TestSession2(ApplicationSession):

    def onJoin(self):
        self.syncing_string = SyncString.create_from_server(self)


class TestSession3(ApplicationSession):

    def onJoin(self):
        self.syncing_string = SyncString.create_from_server(self)
        self.syncing_string.set_string('kyle')
"""