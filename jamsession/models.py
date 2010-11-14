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


class DataSetDefinition(Document):
    title = StringField(unique=True, required=True)
    name = StringField(unique=True, required=True)
    schema = DictField()

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
            data_object_fields[name] = self._field_type_translations.get(field_type, StringField)()

        return data_object_fields

    def get_data_object(self):
        data_object_fields = self._get_data_object_fields()
        return type(
            self.name,
            (Document, ),
            data_object_fields,)
