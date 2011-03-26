import os
import datetime

from django.core.urlresolvers import reverse

from jamsession.test import JamTestCase, JamFuncTestCase


class DataSetTest(JamTestCase):
    def _get_target_class(self):
        from jamsession.models import DataSetDefinition
        return DataSetDefinition

    def test_data_set_basic_schema(self):
        """
        A DataSetDefinition's get_data_set method
        should return an object that has fields
        for every key in it's schema dictionary.
        """
        schema = dict(
            name='string',
            url='url',
            email='email',
            integer='int',
            floater='float',
            boolean='bool',
            datetime='datetime')

        sample_values = dict(
            name='The Doctor',
            url='http://www.doctorwho.com',
            email='the_dr@tardis.time.vortex.co.uk',
            integer=42,
            floater=42.0,
            boolean=True,
            datetime=datetime.datetime(year=1963, month=11, day=23))

        sample_definition = self._make_one(
                name='SampleData',
                schema=schema)

        SampleData = sample_definition.get_data_object()
        s = SampleData(**sample_values)
        s.save()

        s = SampleData.objects.get(id=s.id)
        for key, value in sample_values.items():
            self.assert_(hasattr(s, key))
            self.assertEqual(value, getattr(s, key))

        s2 = SampleData(**sample_values)
        s2.save()
        self.assertEqual(2, SampleData.objects.count())

    def test_duplicate_rows_with_null(self):
        """
        Two Objects created from DynamicDataDefinitions
        should allow two rows to contain null values for the
        same key.
        """
        nullable_schema = {'Archive': 'string',
                           'Backlog': 'string',
                           'Date': 'datetime',
                           'Deploy': 'string',
                           'Development': 'string',
                           'Done': 'string',
                           'Elaboration': 'string',
                           'Ready: Deploy': 'string',
                           'Ready: Dev': 'string',
                           'Ready: Stage': 'string',
                           'Ready: Test': 'string',
                           'Ready: UX': 'string',
                           'Review/Demo': 'string',
                           'Test': 'string',
                           'Training & Marketing': 'string',
                           'UI Dev': 'string',
                           'UX: Backlog': 'string',
                           'UX: Design': 'string',
                           'UX: Elaboration': 'string',
                           'UX: Review/Demo': 'string',
                           'UX: Specification': 'string'}
        NullableDef = self._make_one(name="NullTester",
                                    schema=nullable_schema)

        Nullable = NullableDef.get_data_object()
        Nullable.objects.create(**{'Archive': '0',
                                   'Backlog': '9',
                                   'Date': datetime.datetime(2010, 1, 8),
                                   'Deploy': '16',
                                   'Development': '19',
                                   'Done': '0',
                                   'Elaboration': '1',
                                   'Ready: Deploy': '0',
                                   'Ready: Dev': '0',
                                   'Ready: Stage': '0',
                                   'Ready: Test': '0',
                                   'Ready: UX': '0',
                                   'Review/Demo': '0',
                                   'Test': '23',
                                   'Training & Marketing': '0',
                                   'UI Dev': '0',
                                   'UX: Backlog': '6',
                                   'UX: Design': '2',
                                   'UX: Elaboration': '1',
                                   'UX: Review/Demo': '4',
                                   'UX: Specification': '3'})
        Nullable.objects.create(**{'Archive': '0',
                                   'Backlog': '6',
                                   'Date': datetime.datetime(2010, 1, 8),
                                   'Deploy': '6',
                                   'Development': '22',
                                   'Done': '0',
                                   'Elaboration': '1',
                                   'Ready: Deploy': '0',
                                   'Ready: Dev': '0',
                                   'Ready: Stage': '0',
                                   'Ready: Test': '0',
                                   'Ready: UX': '0',
                                   'Review/Demo': None,
                                   'Test': '22',
                                   'Training & Marketing': '1',
                                   'UI Dev': None,
                                   'UX: Backlog': '5',
                                   'UX: Design': '1',
                                   'UX: Elaboration': '1',
                                   'UX: Review/Demo': '3',
                                   'UX: Specification': '2'})

        self.assertEqual(2, Nullable.objects.count())

    def test_bad_names(self):
        """
        A DataSetDefinition's name may contain
        crazy non-valid Python characters.
        It should appear, unchanged in it's data_object
        repr().
        """
        sample_def = self._make_one(
            name='Bad Fields Object $')

        BadlyNamed = sample_def.get_data_object()
        b = BadlyNamed()
        self.assert_(sample_def.name in repr(b))

    def test_bad_field_names(self):
        from mongoengine import ValidationError
        sample_def = self._make_one(
            name='Crazy Field Names',
            schema={'$foo': 'int',
                    '__baz__': 'url',
                    'hello': 'string', })

        self.assertRaises(ValidationError, sample_def.validate)


class CSVImportTests(JamTestCase):
    def setUp(self):
        self.csv_fixture_path = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),
            'fixtures',)
        super(CSVImportTests, self).setUp()

    def _get_target_class(self):
        from jamsession.models import CSVImporter
        return CSVImporter

    def _get_csv(self, filename):
        return os.path.join(self.csv_fixture_path, filename)

    def _get_cumulative_flow_def(self):
        from jamsession.models import DataSetDefinition
        return DataSetDefinition(
            name='Cumulative Flow Data',
            schema={
                'Date': 'datetime',
                'UX: Backlog': 'int',
                'UX: Elaboration': 'int',
                'UX: Specification': 'int',
                'Backlog': 'int',
                'Elaboration': 'int',
                'Ready: UX': 'int',
                'UX: Design': 'int',
                'UX: Review/Demo': 'int',
                'UI Dev': 'int',
                'Ready: Dev': 'int',
                'Development': 'int',
                'Review/Demo': 'int',
                'Ready: Test': 'int',
                'Test': 'int',
                'Ready: Stage': 'int',
                'Training & Marketing': 'int',
                'Ready: Deploy': 'int',
                'Deploy': 'int',
                'Done': 'int',
                'Archive': 'int', })

    def test_csv_fresh_import(self):
        """
        DataSetDefinitions should be able to load data
        from a CSV into a on-the-fly schema.

        For now, that means all values come in as strings.
        """
        importer = self._make_one()
        datadef, num_created = importer.load(
            self._get_csv('cumulativeflow.csv'))
        DataObj = datadef.get_data_object()

        self.assertEqual(21, len(datadef.schema.keys()))
        self.assert_(DataObj.objects.count() == 91)
        self.assertEqual(91, num_created)

    def test_csv_exisiting_import(self):
        """
        DataSetDefinitions should be able to load data
        from a CSV into an exisiting schema.
        """
        importer = self._make_one()
        datadef = self._get_cumulative_flow_def()
        from jamsession.models import ImportFailed
        import pprint

        try:
            cum_def, num_created = importer.load(self._get_csv(
                    'cumulativeflow.csv'),
                    datadef,)
        except ImportFailed, e:
            pprint.pprint(e.row_errors)
            raise

        DataObj = cum_def.get_data_object()

        self.assertEqual(91, num_created)
        self.assertEqual(91, DataObj.objects.count())


class DataDefFormTests(JamTestCase):
    """Tests for the form to create DataSetDefinitions"""

    def _get_target_klass(self):
        from jamsession.forms.admin import DataDefAdminForm
        return DataDefAdminForm

    def test_name_should_be_required(self):
        Form = self._get_target_klass()
        datas = [
            {'name': None},
            {'name': ''},
            {'name': '   '},
        ]
        for data in datas:
            f = Form(data)
            msg = "Data: %s didn't throw an error" % data
            self.assert_('name' in f.errors.keys(), msg)

        data = {'name': "The Brigadier"}
        f = Form(data)
        assert('name' not in f.errors.keys())

    def test_schema_should_be_required(self):
        Form = self._get_target_klass()
        datas = [
            {'schema': None},
            {'schema': ''},
            {'schema': '   '},
            {'schema': 'Column name'},
        ]
        for data in datas:
            f = Form(data)
            msg = "Data: %s didn't throw an error" % data
            self.assert_('schema' in f.errors.keys(), msg)

        data = {'schema': 'First Name,string'}
        f = Form(data)
        msg = "Data: %s shouldn't have throw any errors, but it did." \
            % (data, )
        self.assert_('schema' not in f.errors.keys(), msg)

    def test_schema_keys_should_be_unique(self):
        Form = self._get_target_klass()
        data = {
            'name': 'Test Dataset',
            'schema': """Name,string
ID,integer
Name,string"""
            }
        f = Form(data)
        assert('schema' in f.errors.keys())

    def test_schema_types_should_be_valid(self):
        Form = self._get_target_klass()
        invalid_datas = [
            {'schema': 'Name,str'},
            {'schema': 'Name,char'},
            {'schema': 'Name,date'},
        ]
        valid_datas = [
            {'schema': 'Name,string'},
            {'schema': 'Name,url'},
            {'schema': 'Name,email'},
            {'schema': 'Name,int'},
            {'schema': 'Name, float'},
            {'schema': 'Name,bool'},
            {'schema': 'Name,datetime'},
         ]

        for data in invalid_datas:
            f = Form(data)
            msg = "Data %s should've created an error but it didn't" % (data, )
            self.assert_('schema' in f.errors.keys(), msg)

        for data in valid_datas:
            f = Form(data)
            self.assert_('schema' not in f.errors.keys())


class DataDefAdminFuncTests(JamFuncTestCase):
    """Functional tests for the admin views."""

    def setUp(self):
        super(DataDefAdminFuncTests, self).setUp()
        self.login()

    def _get_target_klass(self):
        from jamsession.models import DataSetDefinition
        return DataSetDefinition

    def _get_target_url(self):
        return reverse('jamsession:admin-create-object',
                kwargs={'object_type': 'datasetdefinition'})

    def _get_edit_url(self, object_id=None):
        return reverse('jamsession:admin-edit-object',
                       kwargs={'object_type': 'datasetdefinition', 'object_id': object_id})

    def _get_changelist_url(self, object_type='datasetdefinition'):
        return reverse('jamsession:admin-changelist-object',
                       kwargs={'object_type': object_type})

    def test_create_page(self):
        response = self.client.get(self.target_url)
        self.assertContains(response, 'Schema')

    def test_successfull_creation(self):
        klass = self._get_target_klass()
        count = klass.objects.count()

        data = {
            'name': "Test Dataset",
            'schema': """name,string\npay,float\nJob Title,string"""
        }
        response = self.client.post(self.target_url, data)
        self.assertEqual(302, response.status_code)
        new_count = klass.objects.count()
        self.assertEqual(True, new_count - 1 == count)

    def _test_save_handling(self, data_updates, get_expected_url):
        """
        The admin form should fire get_save_url
        get_continue_url and get_addanother_url
        depending on values in request.POST
        or fall back to super()'s get_success_url
        """
        data = {
            'name': 'Tardis',
            'schema': 'name,string'
        }
        data.update(data_updates)

        response = self.client.post(self.target_url, data)

        klass = self._get_target_klass()
        instance = klass.objects.get(name=data['name'])  # Get our object
        expected_url = get_expected_url(instance)
        self.assertRedirects(response, expected_url)

    def test_save_and_add(self):
        data = {'_addanother': "Save and add another"}
        expected_url = lambda i: self.target_url
        self._test_save_handling(data, expected_url)

    def test_save_and_continue(self):
        data = {'_continue': "Save and Continue editing"}
        expected_url = lambda i: self._get_edit_url(i.id)
        self._test_save_handling(data, expected_url)

    def test_save_handling(self):
        data = {'_save': "Save"}
        expected_url = lambda i: self._get_changelist_url()
        self._test_save_handling(data, expected_url)
