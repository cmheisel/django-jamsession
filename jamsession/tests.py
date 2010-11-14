from django.test import TestCase

class DataSetTest(TestCase):
    def setUp(self):
        from mongoengine import connect
        connect('jamsession-unit-tests')

    def tearDown(self):
        from mongoengine.connection import _get_db
        db = _get_db()
        db.drop_collection('jamsession-unit-tests')

    def _get_target_class(self):
        from jamsession.models import DataSetDefinition
        return DataSetDefinition

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_data_set_basic_schema(self):
        """
        A DataSetDefinition's get_data_set method
        should return an object that has fields
        for every key in it's schema dictionary.
        """
        import datetime

        schema = dict(
            name = 'string',
            url = 'url',
            email = 'email',
            integer = 'int',
            floater = 'float',
            boolean = 'bool',
            datetime = 'datetime')

        sample_values = dict(
            name = 'The Doctor',
            url = 'http://www.doctorwho.com',
            email = 'the_dr@tardis.time.vortex.co.uk',
            integer = 42,
            floater = 42.0,
            boolean = True,
            datetime = datetime.datetime(year=1963, month=11, day=23))

        sample_definition = self._make_one(
                name = 'SampleData',
                schema = schema)

        SampleData = sample_definition.get_data_object()
        s = SampleData(**sample_values)
        s.save()

        s = SampleData.objects.get(id=s.id)
        for key, value in sample_values.items():
            self.assert_(hasattr(s, key))
            self.assertEqual(value, getattr(s, key))


    def test_bad_names(self):
        """
        A DataSetDefinition's name may contain
        crazy non-valid Python characters.
        It should appear, unchanged in it's data_object
        repr().
        """
        sample_def = self._make_one(
            name = 'Bad Fields Object $')

        BadlyNamed = sample_def.get_data_object()
        b = BadlyNamed()
        self.assert_(sample_def.name in repr(b))

    def test_bad_field_names(self):
        from jamsession.models import ValidationError
        sample_def = self._make_one(
            name = 'Crazy Field Names',
            schema = { '$foo': 'int',
                       '__baz__': 'url',
                       'hello': 'string', })

        self.assertRaises(ValidationError, sample_def.validate)
