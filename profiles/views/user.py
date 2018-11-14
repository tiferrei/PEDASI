from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView


class UserProfileView(DetailView):
    template_name = 'profiles/user/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user


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
