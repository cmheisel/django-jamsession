from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.sites import site
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.create_update import create_object as generic_create_object

from jamsession.models import DataSetDefinition
from jamsession.forms.admin import DataDefAdminForm


@site.admin_view
def dashboard(request):
    """
    Dashboard view for Jamsession app.
    """
    context = {
        'title': "Jamsession Administration",
    }
    return render_to_response(
        'jamsession/admin/dashboard.html',
        context,
        context_instance=RequestContext(request))


object_types = {
    'datasetdefinition': (DataSetDefinition, DataDefAdminForm)
}


@site.admin_view
def create_object(request, object_type):
    klass, form_klass = object_types.get(object_type, None)
    if not klass:
        raise Http404("Content type %s not found" % object_type)

    form_class = form_klass
    post_save_url = reverse("jamsession:admin-edit-object",
                            kwargs=dict(object_type=object_type,
                                        object_id="%(id)s")
    )
    template_name = 'jamsession/admin/create_object.html'
    context = {
        'title': 'Add %s' % klass.verbose_name,
        'klass': klass,
        'add': True,
        'obj': None,
    }
    return generic_create_object(request,
                                 form_class=form_class,
                                 template_name=template_name,
                                 extra_context=context,
                                 post_save_redirect=post_save_url)


def edit_object(request, object_type, object_id):
    pass
