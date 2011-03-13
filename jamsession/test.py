from unittest2 import TestCase

from django.test import TestCase as DjangoTestCase
from django.test.client import RequestFactory


class JamTestCaseBase(DjangoTestCase, TestCase):
    """
    Base TestCase using encompassing functionality from
    both Django and unittest2
    """
    def setUp(self):
        from mongoengine import connect
        connect('jamsession-unit-tests')
        super(JamTestCaseBase, self).setUp()

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
    def setUp(self):
        self.factory = RequestFactory()
        self.username = 'test'
        self.email = 'test@test.test'
        self.password = 'test'
        self._set_up_user()
        super(JamFuncTestCase, self).setUp()

    def _set_up_user(self):
        from django.contrib.auth.models import User
        u = User.objects.create_user(self.username, self.email, self.password)
        u.is_staff = True
        u.save()

    def login(self):
        result = self.client.login(username=self.username, password=self.password)
        self.assert_(result)

    def _get_target_url(self):
        raise NotImplementedError

    @property
    def target_url(self):
        return self._get_target_url()
