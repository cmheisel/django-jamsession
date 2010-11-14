from mongoengine import (
    Document,
    StringField,
    ListField,
    GenericReferenceField,
    DictField,
    EmailField,
)

class DynamicSchema(Document):
    title = StringField(unique=True, required=True)
    name = StringField(unique=True, required=True)
    schema = DictField()

    def get_data_access_object(self):
        return type(
            self.name,
            (Document, ),
            { "name": StringField(),
              "title": StringField(),
              "email": EmailField(),
            })
