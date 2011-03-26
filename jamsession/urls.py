from django.conf.urls.defaults import *

from jamsession.views.admin import (DashboardView,
                                    AdminCreateView,
                                    edit_object,
                                    changelist
                                    )

urlpatterns = patterns('',
    url(r'^admin/$', DashboardView.as_view(), name="admin-dashboard"),
    url(r'^admin/(?P<object_type>\w+)/add/$', AdminCreateView.as_view(), name='admin-create-object'),
    url(r'^admin/(?P<object_type>\w+)/edit/(?P<object_id>(.*?))/$', edit_object, name='admin-edit-object'),
    url(r'^admin/(?P<object_type>\w+)/$', changelist, name='admin-changelist-object'),
)
