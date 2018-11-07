from django.contrib.auth import get_user_model
from django.db.models import F
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse, QueryDict
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView

import requests.exceptions

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_edit_permission'] = self.request.user.is_staff or self.request.user == self.object.owner

        return context


class DataSourceDataSetSearchView(DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/dataset_search.html'
    context_object_name = 'datasource'

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except requests.exceptions.HTTPError as e:
            return HttpResponse(
                'API call failed',
                # Pass status code through unless it was 200 OK
                status=424 if e.response.status_code == 200 else e.response.status_code
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        connector = self.object.data_connector
        try:
            datasets = list(connector.items(
                params={
                    'prefix-val': self.request.GET.get('q')
                }
            ))
            context['datasets'] = datasets

            # Check the metadata format of the first dataset
            # TODO will all metadata formats be the same
            if isinstance(datasets[0][1].get_metadata(), list):
                context['metadata_type'] = 'list'
            else:
                context['metadata_type'] = 'dict'

        except AttributeError:
            # DataSource is not a catalogue
            pass

        return context


class DataSourceAccessManageView(OwnerPermissionRequiredMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/manage_access.html'
    context_object_name = 'datasource'

    permission_required = 'datasources.change_datasource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_users'] = get_user_model().objects

        context['permissions_requested'] = models.UserPermissionLink.objects.filter(
            datasource=self.object,
            requested__gt=F('granted')
        )
        context['permissions_granted'] = models.UserPermissionLink.objects.filter(
            datasource=self.object,
            requested__lte=F('granted'),
            granted__gt=models.UserPermissionLevels.NONE
        )

        return context


class DataSourceAccessGrantView(SingleObjectMixin, View):
    """
    Manage a user's access to a DataSource.

    Accepts PUT and DELETE requests to add a user to, or remove a user from the access group.
    Request responses follow JSend specification (see http://labs.omniti.com/labs/jsend).
    """
    model = models.DataSource

    def _set_permission(self, user, level=models.UserPermissionLevels.VIEW):
        if level == models.UserPermissionLevels.NONE:
            try:
                permission = models.UserPermissionLink.objects.get(
                    user=user,
                    datasource=self.get_object(),
                )
                permission.delete()

            except models.UserPermissionLink.DoesNotExist:
                pass

            return None

        try:
            permission = models.UserPermissionLink.objects.get(
                user=user,
                datasource=self.get_object(),
            )

            permission.granted = level
            permission.requested = max(permission.requested, level)
            permission.save()

        except models.UserPermissionLink.DoesNotExist:
            permission = models.UserPermissionLink.objects.create(
                user=user,
                datasource=self.get_object(),
                granted=level,
                requested=level
            )

        return permission

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
        data = QueryDict(request.body)
        user = get_user_model().objects.get(pk=data['user'])

        try:
            level = models.UserPermissionLevels(
                int(data['level'])
            )

        except KeyError:
            level = models.UserPermissionLevels.VIEW

        permission = self._set_permission(
            user,
            level=level
        )

        if permission is None:
            return JsonResponse({
                'status': 'success',
                'data': None
            })

        return JsonResponse({
            'status': 'success',
            'data': {
                'permission': {
                    'pk': permission.pk,
                    'user': permission.user_id,
                    'datasource': permission.datasource_id,
                    'granted': permission.granted,
                    'requested': permission.requested,
                },
            },
        })


class DataSourceAccessRequestView(SingleObjectMixin, View):
    """
    Manage a user's access to a DataSource.

    Accepts PUT and DELETE requests to add a user to, or remove a user from the access group.
    Request responses follow JSend specification (see http://labs.omniti.com/labs/jsend).
    """
    model = models.DataSource

    def _request_permission(self, user, level):
        if level == models.UserPermissionLevels.NONE:
            try:
                permission = models.UserPermissionLink.objects.get(
                    user=user,
                    datasource=self.get_object(),
                )
                permission.delete()

            except models.UserPermissionLink.DoesNotExist:
                pass

            return None

        try:
            permission = models.UserPermissionLink.objects.get(
                user=user,
                datasource=self.get_object()
            )

            permission.requested = level
            permission.save()

        except models.UserPermissionLink.DoesNotExist:
            permission = models.UserPermissionLink.objects.create(
                user=user,
                datasource=self.get_object(),
                requested=level
            )

        return permission

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
        data = QueryDict(request.body)

        try:
            level = models.UserPermissionLevels(
                int(data['level'])
            )

        except KeyError:
            level = models.UserPermissionLevels.VIEW

        permission = self._request_permission(
            request.user,
            level=level
        )

        if permission is None:
            return JsonResponse({
                'status': 'success',
                'data': None
            })

        return JsonResponse({
            'status': 'success',
            'data': {
                'permission': {
                    'pk': permission.id,
                    'user': permission.user_id,
                    'datasource': permission.datasource_id,
                    'granted': permission.granted,
                    'requested': permission.requested,
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
            params={'year': 2018}
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


class DataSourceExploreView(HasViewPermissionMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/explore.html'
    context_object_name = 'datasource'
