from mongoengine import (
    StringField,
    URLField,
    EmailField,
    IntField,
    FloatField,
    BooleanField,
    DateTimeField,
)


FIELD_TYPE_TRANSLATIONS = {
    'string': StringField,
    'url': URLField,
    'email': EmailField,
    'int': IntField,
    'float': FloatField,
    'bool': BooleanField,
    'datetime': DateTimeField
}
