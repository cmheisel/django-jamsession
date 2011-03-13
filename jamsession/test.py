from unittest2 import TestCase

from django.test import TestCase as DjangoTestCase

class JamTestCaseBase(DjangoTestCase, TestCase):
    """
    Base TestCase using encompassing functionality from
    both Django and unittest2
    """
    def setUp(self):
        from mongoengine import connect
        connect('jamsession-unit-tests')

    def tearDown(self):
        from mongoengine.connection import _get_db
        db = _get_db()
        #Wipe out our test db
        [db.drop_collection(name) for name in db.collection_names() \
          if 'system.' not in name]


class JamTestCase(JamTestCaseBase):
    def _get_target_class(self):
        raise NotImplementedError

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


class JamFuncTestCase(JamTestCaseBase):
    pass
