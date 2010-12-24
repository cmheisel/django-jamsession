from django.conf.urls.defaults import *

from jamsession.views.admin import (dashboard, create_object)

urlpatterns = patterns('',
    url(r'^admin/$', dashboard, name="admin-dashboard"),
    url(r'^admin/create/(?P<object_type>\w+)/$', create_object, name='admin-create-object'),
)
