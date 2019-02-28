"""
Views to manage user profiles.
"""

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from rest_framework.authtoken.models import Token

from applications.models import Application
from datasources.models import DataSource
from profiles.permissions import SelfOrAdminPermissionMixin


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Add recent Applications and DataSources to index page.

        :return: Django context dictionary
        """
        context = super().get_context_data(**kwargs)

        context['datasources'] = DataSource.objects.order_by('-external_requests')[:6]
        context['applications'] = Application.objects.order_by('-id')[:3]

        return context


class UserProfileView(DetailView):
    template_name = 'profiles/user/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class UserUriView(DetailView):
    """
    View providing verification that a PEDASI User URI exists.
    """
    model = get_user_model()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse({
            'status': 'success',
            'data': {
                'user': {
                    'pk': self.object.pk,
                }
            }
        })


class UserInactiveView(TemplateView):
    template_name = 'profiles/user/inactive.html'


class UserManageTokenView(SelfOrAdminPermissionMixin, DetailView):
    """
    Manage an API Token for the requested user.
    """
    model = get_user_model()

    def render_to_response(self, context, **response_kwargs):
        """
        Get an existing API Token or create a new one for the requested user.

        :return: JSON containing Token key
        """
        api_token, created = Token.objects.get_or_create(user=self.object)

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
        Revoke an API Token for the requested user.
        """
        self.object = self.get_object()
        self.object.revoke_auth_token()

        return JsonResponse({
            'status': 'success',
            'data': {
                'token': None,
            }
        })
