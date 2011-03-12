from django.forms import CharField


class SchemaField(CharField):
    """
    Custom field to accept a comma and line delimited
    text input of a schema definition
    """
    def to_python(self, value):
        if value:
            value = value.strip()
        if not value:
            return {}
        return value
