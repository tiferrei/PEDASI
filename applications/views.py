"""
Views to manage and access :class:`Application`s.
"""

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from rest_framework.authtoken.models import Token

from . import models
from core.views import ManageAccessView
from profiles.permissions import OwnerPermissionMixin


class ApplicationListView(ListView):
    model = models.Application
    template_name = 'applications/application/list.html'
    context_object_name = 'applications'


class ApplicationCreateView(PermissionRequiredMixin, CreateView):
    model = models.Application
    template_name = 'applications/application/create.html'
    context_object_name = 'application'

    fields = '__all__'
    permission_required = 'applications.add_application'

    def form_valid(self, form):
        try:
            owner = form.instance.owner

        except models.Application.owner.RelatedObjectDoesNotExist:
            form.instance.owner = self.request.user

        return super().form_valid(form)


class ApplicationUpdateView(OwnerPermissionMixin, UpdateView):
    model = models.Application
    template_name = 'applications/application/update.html'
    context_object_name = 'application'

    fields = '__all__'
    permission_required = 'applications.change_application'


class ApplicationDeleteView(OwnerPermissionMixin, DeleteView):
    model = models.Application
    template_name = 'applications/application/delete.html'
    context_object_name = 'application'

    permission_required = 'applications.delete_application'
    success_url = reverse_lazy('applications:application.list')


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
            try:
                context['api_key'] = self.object.proxy_user.auth_token

            except Token.DoesNotExist:
                pass

        return context


class ApplicationManageAccessView(OwnerPermissionMixin, ManageAccessView):
    """
    Manage a user's access to a Application.

    On GET request will display the access management page.
    Accepts PUT and DELETE requests to add a user to, or remove a user from the access group.
    Request responses follow JSend specification (see http://labs.omniti.com/labs/jsend).
    """
    model = models.Application
    template_name = 'applications/application/manage_access.html'
    context_object_name = 'application'


class ApplicationManageTokenView(OwnerPermissionMixin, DetailView):
    """
    Manage an API Token for an application.
    """
    model = models.Application

    def render_to_response(self, context, **response_kwargs):
        """
        Get an existing API Token or create a new one for the requested :class:`Application`.

        :return: JSON containing Token key
        """
        api_token, created = Token.objects.get_or_create(user=self.object.proxy_user)

        return JsonResponse({
            'status': 'success',
            'data': {
                'token': {
                    'key': api_token.key
                }
            }
        })

    def delete(self, request, *args, **kwargs):
        """
        Revoke an API Token for the requested :class:`Application`.
        """
        self.object = self.get_object()
        self.object.proxy_user.revoke_auth_token()

        return JsonResponse({
            'status': 'success',
            'data': {
                'token': None,
            }
        })
