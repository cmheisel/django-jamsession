from django import forms

from jamsession.forms.fields import SchemaField
from jamsession.models import Schema


class SchemaAdminForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    name = forms.CharField(required=True,
                           widget=forms.TextInput(
                           attrs={'class': 'vTextField'})
                           )
    schema = SchemaField(widget=forms.Textarea, required=True)

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            self.instance = kwargs['instance']
            del kwargs['instance']

        super(SchemaAdminForm, self).__init__(*args, **kwargs)

    class _meta(object):
        model = Schema

    def clean_name(self):
        data = self.cleaned_data['name'].strip()
        if not data:
            raise forms.ValidationError("Name is required.")

        if self._meta.model.objects.filter(name=data).count() >= 1:
            raise forms.ValidationError("Name must be unique.")
        return data

    def save(self):
        obj = self._meta.model(**self.cleaned_data)
        obj.save()
        return obj
