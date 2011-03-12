from django.forms import CharField


class SchemaField(CharField):
    """
    Custom field to accept a comma and line delimited
    text input of a schema definition
    """
    def parse_schema_entries(self, text):
        lines = [line for line in text.split('\n')]
        schema = {}

        for line in lines:
            parts = line.split(',')
            if len(parts) >= 2:
                key, value = parts[0].strip(), parts[1].strip()
                if key and value: schema[key] = value

        return schema

    def to_python(self, value):
        if value:
            value = value.strip()
        if not value:
            return {}
        return self.parse_schema_entries(value)
