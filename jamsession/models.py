import os
import sys
import logging
import pprint
from csv import DictReader

from mongoengine import (
    Document,
    StringField,
    URLField,
    EmailField,
    IntField,
    FloatField,
    BooleanField,
    DateTimeField,
    DictField,
)

from django import forms


class SchemaDefinitionField(DictField):
    def validate(self, value):
        return super(SchemaDefinitionField, self).validate(value)


class ClassProperty(property):
        def __get__(self, cls, owner):
                return self.fget.__get__(None, owner)()


class DocumentModel(Document):
    @classmethod
    def verbose_name(cls):
        return cls.meta.get('verbose_name', cls.__name__)
    verbose_name = ClassProperty(verbose_name)

    @classmethod
    def verbose_name_plural(cls):
        return cls.meta.get('verbose_name_plural', cls.verbose_name + 's')
    verbose_name_plural = ClassProperty(verbose_name_plural)

    @classmethod
    def app_label(cls):
        app_label = cls.meta.get('app_label', None)
        if not app_label:
            model_module = sys.modules[cls.__module__]
            app_label = model_module.__name__.split('.')[-2]
        return app_label
    app_label = ClassProperty(app_label)

    @classmethod
    def object_name(cls):
        return cls.meta.get('object_name', cls.__name__)
    object_name = ClassProperty(object_name)


class DataSetDefinition(DocumentModel):
    name = StringField(unique=True, required=True)
    schema = SchemaDefinitionField()
    meta = {
        'verbose_name': 'Data set definition'
    }

    _field_type_translations = {
        'string': StringField,
        'url': URLField,
        'email': EmailField,
        'int': IntField,
        'float': FloatField,
        'bool': BooleanField,
        'datetime': DateTimeField}

    def _get_data_object_fields(self):
        data_object_fields = {}
        for name, field_type in self.schema.items():
            data_object_fields[name] = \
                self._field_type_translations[field_type]()

        return data_object_fields

    def _get_data_object_name(self):
        parts = [part.strip().capitalize() for part in self.name.split('.')]
        return ''.join(parts)

    def get_data_object(self):
        self.validate()
        data_object_fields = self._get_data_object_fields()

        def data_object_repr(obj):
            return u"<%s: %s>" % (obj.__class__, self.name)
        data_object_fields['__repr__'] = data_object_repr

        return type(
            self._get_data_object_name(),
            (DocumentModel, ),
            data_object_fields,)

    class AdminForm(forms.Form):
        error_css_class = 'error'
        required_css_class = 'required'
        name = forms.CharField(required=True)

        def save(self):
            obj = DataSetDefinition(**self.cleaned_data)
            obj.save()
            return obj


class ImportFailed(Exception):
    row_errors = []


class ImportConversionFailed(Exception):
    errors = []


class CSVImporter(object):
    def __init__(self):
        super(CSVImporter, self).__init__()
        self.logger = logging.getLogger("jamsession.CSVImporter")

    @property
    def converters(self):
        return {
            'string': str,
            'url': str,
            'email': str,
            'int': int,
            'float': float,
            'bool': bool,
            'datetime': self.cast_datetime, }

    def cast_datetime(self, value):
        from dateutil.parser import parse
        return parse(value)

    def cast_value(self, value, typehint):
        if value in ('', u'', None):
            return None
        return self.converters[typehint](value)

    def prepare_row(self, row, schema):
        cast_row = {}
        errors = []
        for key in row.keys():
            try:
                cast_row[key] = self.cast_value(row[key], schema[key])
            except TypeError:
                errors.append("Couldn't convert < %s > to %s"
                              % (row[key], schema[key]))
        if errors:
            exc = ImportConversionFailed("Couldn't convert row %s" % row)
            exc.errors = errors
            raise exc
        return cast_row

    def check_columns(self, reader, datadef):
        # First do the columns even match?
        import_columns = [name.strip()
                           for name in reader.fieldnames]
        target_columns = datadef.schema.keys()

        for col in import_columns:
            if col not in target_columns:
                msg = ["Column's don't match target schema:",
                       "TARGET COLUMNS",
                       "%s" % target_columns,
                       "",
                       "IMPORT COLUMNS",
                       "%s" % import_columns, ]
                msg = '\n'.join(msg)
                raise ImportFailed(msg)

    def load(self, datafile, datadef=None):
        """
        Read a CSV file into a new (all-strings) schema.
        Optionally accepts an existing DataSetDefinition.

        If the entire CSV can not be loaded, the operation will
        be aborted and an ImportFailed exception will be raised.
        """
        reader = DictReader(file(datafile, 'r'))

        if not datadef:
            schema = [(name.strip(), 'string') for name in reader.fieldnames]
            datadef = DataSetDefinition.objects.create(
                name=os.path.basename(datafile),
                schema=dict(schema))
            datadef.save()

        self.check_columns(reader, datadef)

        Obj = datadef.get_data_object()
        logging.debug(type(Obj))
        logging.debug(dir(Obj))
        logging.debug(Obj._class_name)
        row_errors = []
        values = []
        for row in reader:
            try:
                values.append(self.prepare_row(row, datadef.schema))
            except ImportConversionFailed, e:
                row_errors.append((row, e.errors))

        if row_errors:
            exc = ImportFailed(
                "Failed to import entire file, %s rows had errors"
                % len(row_errors))
            exc.row_errors = row_errors
            raise exc

#        new_objects = [Obj.objects.create(**v) for v in values if v]

        new_objects = []
        for v in values:
            self.logger.debug("Creating row with values %s"
                              % pprint.pformat(v))
            new_objects.append(Obj.objects.create(**v))
            self.logger.debug("SUCCESS!")

        return (datadef, len(new_objects))
