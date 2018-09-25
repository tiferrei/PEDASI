from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import models


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


class ApplicationManageAccessView(DetailView):
    """
    Manage a user's access to a Application.

    On GET request will display the access management page.
    Accepts PUT and DELETE requests to add a user to, or remove a user from the access group.
    Request responses follow JSend specification (see http://labs.omniti.com/labs/jsend).
    """
    model = models.Application
    template_name = 'applications/application/manage_access.html'
    context_object_name = 'application'

    def put(self, request, *args, **kwargs):
        """
        Add a user to the access group for a Application.

        If the request is performed by the Application owner or by staff: add them directly to the access group,
        If the request is performed by the user themselves: add them to the 'access requested' group,
        Else reject the request.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.request = request
        self.object = self.get_object()

        user = get_user_model().objects.get(pk=kwargs['user_pk'])
        access_group = self.object.users_group
        request_group = self.object.users_group_requested

        if self.request.user == self.object.owner or self.request.user.is_staff:
            # If request is from Application owner or staff, add user to access group
            access_group.user_set.add(user)
            request_group.user_set.remove(user)

        elif self.request.user == user:
            if access_group.user_set.filter(id=user.id).exists():
                return HttpResponseBadRequest(
                    JsonResponse({
                        'status': 'fail',
                        'message': 'You already have access to this resource',
                    })
                )

            # If user is requesting for themselves, add them to 'access requested' group
            request_group.user_set.add(user)

        else:
            return HttpResponseForbidden(
                JsonResponse({
                    'status': 'fail',
                    'message': 'You do not have permission to set access for this user',
                })
            )

        return JsonResponse({
            'status': 'success',
            'data': {
                'user': {
                    'pk': user.pk
                },
            },
        })

    def delete(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_object()

        user = get_user_model().objects.get(pk=kwargs['user_pk'])
        access_group = self.object.users_group
        request_group = self.object.users_group_requested

        if self.request.user == user or self.request.user == self.object.owner or self.request.user.is_staff:
            # Users can remove themselves, be removed by the Application owner, or by staff
            access_group.user_set.remove(user)
            request_group.user_set.remove(user)

        else:
            return HttpResponseForbidden(
                JsonResponse({
                    'status': 'fail',
                    'message': 'You do not have permission to set access for this user',
                })
            )

        return JsonResponse({
            'status': 'success',
            'data': {
                'user': {
                    'pk': user.pk
                },
            },
        })
