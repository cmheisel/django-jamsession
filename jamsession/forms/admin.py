from django import forms

from jamsession.forms.fields import SchemaField
from jamsession.models import DataSetDefinition


class DataDefAdminForm(forms.Form):
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

        super(DataDefAdminForm, self).__init__(*args, **kwargs)

    class _meta(object):
        model = DataSetDefinition

    def clean_name(self):
        data = self.cleaned_data['name'].strip()
        if not data:
            raise forms.ValidationError("Name is required.")
        return data

    def save(self):
        obj = DataSetDefinition(**self.cleaned_data)
        obj.save()
        return obj
