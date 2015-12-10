from __future__ import unicode_literals
import pytest
import autopubpy.models

def test_offline_one():
    test_list = autopubpy.models.SyncList()
    test_dict = autopubpy.models.SyncDict()
    test_ordereddict = autopubpy.models.SyncOrderedDict()


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

if __name__ == "__main__":
    import pytest
    options = ['-s']
    dirs = [__file__]
    arguments = options + dirs
    exitcode = pytest.main(arguments)
    raw_input()