from django.contrib import admin
from jamsession.models import DataSetDefinition


class DataSetDefinitionAdmin(admin.ModelAdmin):
    pass

admin.site.register([DataSetDefinition], DataSetDefinitionAdmin)
