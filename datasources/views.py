from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView

from profiles.permissions import HasViewPermissionMixin, OwnerPermissionRequiredMixin
from datasources import models


class DataSourceListView(ListView):
    model = models.DataSource
    template_name = 'datasources/datasource/list.html'
    context_object_name = 'datasources'


class DataSourceDetailView(DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/detail.html'
    context_object_name = 'datasource'

    def get_template_names(self):
        if not self.object.has_view_permission(self.request.user):
            return ['datasources/datasource/detail-no-access.html']
        return super().get_template_names()


class DataSourceManageAccessView(OwnerPermissionRequiredMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/manage_access.html'
    context_object_name = 'datasource'

    permission_required = 'datasources.change_datasource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_users'] = get_user_model().objects

        return context


class DataSourceRequestAccessView(SingleObjectMixin, View):
    """
    Manage a user's access to a DataSource.

    Accepts PUT and DELETE requests to add a user to, or remove a user from the access group.
    Request responses follow JSend specification (see http://labs.omniti.com/labs/jsend).
    """
    model = models.DataSource

    def put(self, request, *args, **kwargs):
        """
        Add a user to the access group for a DataSource.

        If the request is performed by the DataSource owner or by staff: add them directly to the access group,
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
            # If request is from DataSource owner or staff, add user to access group
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
            # Users can remove themselves, be removed by the DataSource owner, or by staff
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


class DataSourceQueryView(HasViewPermissionMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/query.html'
    context_object_name = 'datasource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['results'] = self.object.data_connector.get_data(
            query_params={'year': 2018}
        )

        return context


class DataSourceMetadataView(HasViewPermissionMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/metadata.html'
    context_object_name = 'datasource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Using data connector context manager saves API queries
        with self.object.data_connector as dc:
            context['metadata'] = dc.get_metadata()
            context['datasets'] = {
                dataset: dc.get_metadata(dataset)
                for dataset in dc.get_datasets()
            }

        return context
