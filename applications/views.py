from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import models

from core.views import ManageAccessView


class ApplicationListView(ListView):
    model = models.Application
    template_name = 'applications/application/list.html'
    context_object_name = 'applications'


class ApplicationDetailView(DetailView):
    model = models.Application
    template_name = 'applications/application/detail.html'
    context_object_name = 'application'

    def get_template_names(self):
        if not self.object.has_view_permission(self.request.user):
            return ['applications/application/detail-no-access.html']
        return super().get_template_names()


class ApplicationManageAccessView(ManageAccessView):
    """
    Manage a user's access to a Application.

    On GET request will display the access management page.
    Accepts PUT and DELETE requests to add a user to, or remove a user from the access group.
    Request responses follow JSend specification (see http://labs.omniti.com/labs/jsend).
    """
    model = models.Application
    template_name = 'applications/application/manage_access.html'
    context_object_name = 'application'
