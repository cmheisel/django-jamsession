import string

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
from mongoengine.base import ValidationError

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

from csv import DictReader
import os

class CSVImporter(object):
    def load(self, datafile, datadef=None, has_fieldnames=True):
        reader = DictReader(file(datafile, 'r'))

        if not datadef:
            schema = [(name, 'string') for name in reader.fieldnames]
            datadef = DataSetDefinition.objects.create(
                name = os.path.basename(datafile),
                schema = dict(schema))
            datadef.save()

        return datadef

