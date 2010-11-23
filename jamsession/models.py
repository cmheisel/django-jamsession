import os
from csv import DictReader

import dateutil

from mongoengine import ValidationError

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

class SchemaDefinitionField(DictField):
    def validate(self, value):
        return super(SchemaDefinitionField, self).validate(value)

class DataSetDefinition(Document):
    name = StringField(unique=True, required=True)
    schema = SchemaDefinitionField()

    _field_type_translations = {
        'string': StringField,
        'url': URLField,
        'email': EmailField,
        'int': IntField,
        'float': FloatField,
        'bool': BooleanField,
        'datetime': DateTimeField }

    def _get_data_object_fields(self):
        data_object_fields = {}
        for name, field_type in self.schema.items():
            data_object_fields[name] = self._field_type_translations[field_type]()

        return data_object_fields

    def get_data_object(self):
        self.validate()
        data_object_fields = self._get_data_object_fields()

        def data_object_repr(obj):
            return u"<%s: %s>" % (obj.__class__, self.name)
        data_object_fields['__repr__'] = data_object_repr

        return type(
            'DynamicDataObject',
            (Document, ),
            data_object_fields,)

class ImportFailed(Exception):
    row_errors = []

class ImportConversionFailed(Exception):
    errors = []

class CSVImporter(object):
    @property
    def converters(self):
        import datetime
        return {
            'string': str,
            'url': str,
            'email': str,
            'int': int,
            'float': float,
            'bool': bool,
            'datetime': self.cast_datetime,}

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
                errors.append("Couldn't convert < %s > to %s" % (row[key], schema[key]))
        if errors:
            exc = ImportConversionFailed("Couldn't convert row %s" % row)
            exc.errors = errors
            raise exc
        return cast_row

    def check_columns(self, reader, datadef):
        # First do the columns even match?
        import_columns = [ name.strip() for name in reader.fieldnames ]
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
                name = os.path.basename(datafile),
                schema = dict(schema))
            datadef.save()

        self.check_columns(reader, datadef)

        Obj = datadef.get_data_object()
        row_errors = []
        values = []
        for row in reader:
            try:
                values.append(self.prepare_row(row, datadef.schema))
            except ImportConversionFailed, e:
                row_errors.append((row, e.errors))

        if row_errors:
            exc = ImportFailed(
                "Failed to import entire file, %s rows had errors" % len(row_errors))
            exc.row_errors = row_errors
            raise exc

        new_objects = [ Obj.objects.create(**v) for v in values ]
        return (datadef, len(new_objects))

