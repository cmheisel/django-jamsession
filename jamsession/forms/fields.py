import pprint

from django import forms

from jamsession.util import FIELD_TYPE_TRANSLATIONS


class SchemaField(forms.CharField):
    """
    Custom field to accept a comma and line delimited
    text input of a schema definition
    """

    def validate_key_value_pairs(self, key, value, schema):
        if not(key and value):
            msg = "Must provide both a column name and a column type"
            raise forms.ValidationError(msg)
        if key in schema.keys():
            msg = "Column names must be unique, more than one %s defined" % key
            raise forms.ValidationError(msg)

        valid_values = FIELD_TYPE_TRANSLATIONS.keys()
        if value not in valid_values:
            print "<%s> not in %s" % (key, valid_values)
            msg = "Column types must be one of %s, got %s" % \
                (pprint.pformat(valid_values), key)
            raise forms.ValidationError(msg)
        return True

    def parse_schema_entries(self, text):
        lines = [line for line in text.split('\n')]
        schema = {}

        for line in lines:
            parts = line.split(',')
            if len(parts) >= 2:
                key, value = parts[0].strip(), parts[1].strip()
                self.validate_key_value_pairs(key, value, schema)
                schema[key] = value
        return schema

    def to_python(self, value):
        if value:
            value = value.strip()
        if not value:
            return {}
        return self.parse_schema_entries(value)
