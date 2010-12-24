from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.sites import site
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from jamsession.models import DataSetDefinition


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
    'datasetdefinition': DataSetDefinition,
}


@site.admin_view
def create_object(request, object_type):
    klass = object_types.get(object_type, None)
    if not klass:
        raise Http404

    form_class = klass.AdminForm

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            obj_id = form.save()
            return HttpResponseRedirect(reverse("jamsession:admin-edit",
                                                kwargs=dict(object_id=obj_id)))
    else:
        obj = None
        form = form_class()

    context = {
        'title': 'Add %s' % klass.verbose_name,
        'form': form,
        'klass': klass,
        'add': True,
        'obj': obj,
    }
    return render_to_response('jamsession/admin/create_object.html',
                              context,
                              context_instance=RequestContext(request),)
