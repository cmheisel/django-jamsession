from django.conf.urls.defaults import *

from jamsession.views.admin import (dashboard, )

urlpatterns = patterns('',
    url(r'^admin/$', dashboard, name="jamadmin-dashboard"),
)
