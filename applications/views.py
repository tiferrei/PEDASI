from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from rest_framework.authtoken.models import Token

from . import models
from core.views import ManageAccessView


class ApplicationListView(ListView):
    model = models.Application
    template_name = 'applications/application/list.html'
    context_object_name = 'applications'


class ApplicationCreateView(CreateView):
    model = models.Application
    template_name = 'applications/application/create.html'
    context_object_name = 'application'

    fields = '__all__'

    def form_valid(self, form):
        try:
            owner = form.instance.owner

        except models.Application.owner.RelatedObjectDoesNotExist:
            form.instance.owner = self.request.user

        return super().form_valid(form)


class ApplicationUpdateView(UpdateView):
    model = models.Application
    template_name = 'applications/application/update.html'
    context_object_name = 'application'

    fields = '__all__'


class ApplicationDetailView(DetailView):
    model = models.Application
    template_name = 'applications/application/detail.html'
    context_object_name = 'application'

    def get_template_names(self):
        if not self.object.has_view_permission(self.request.user):
            return ['applications/application/detail-no-access.html']
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_edit_permission'] = self.request.user.is_superuser or self.request.user == self.object.owner

        if self.request.user == self.object.owner or self.request.user.is_superuser:
            context['api_key'] = Token.objects.get(user=self.object.proxy_user)

        return context


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
