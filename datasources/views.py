from django.contrib.auth import get_user_model
from django.db.models import F, ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import reverse
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

import requests.exceptions

from . import forms
from datasources import models
from profiles.permissions import HasViewPermissionMixin, OwnerPermissionRequiredMixin


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


class DataSourceAccessGrantView(UpdateView):
    """
    Manage a user's access to a DataSource.

    Provides a form view to edit permissions, but permissions may also be set using an AJAX POST request.
    """
    model = models.UserPermissionLink
    form_class = forms.PermissionGrantForm
    template_name = 'datasources/user_permission_link/form.html'

    def get_context_data(self, **kwargs):
        """
        Add data source to the context.
        """
        context = super().get_context_data()

        context['datasource'] = models.DataSource.objects.get(pk=self.kwargs['pk'])

        return context

    def get_object(self, queryset=None):
        """
        Get or create a permission object for the relevant user.
        """
        self.datasource = models.DataSource.objects.get(pk=self.kwargs['pk'])

        if self.request.method == 'POST':
            user = get_user_model().objects.get(id=self.request.POST.get('user'))

        else:
            user = get_user_model().objects.get(id=self.request.GET.get('user'))

        obj, created = self.model.objects.get_or_create(
            user=user,
            datasource=self.datasource
        )

        return obj

    def get_success_url(self):
        """
        Return to access management view.
        """
        return reverse('datasources:datasource.access.manage', kwargs={'pk': self.datasource.pk})


class DataSourceAccessRequestView(UpdateView):
    """
    Request access to a data source, or request changes to an existing permission.

    Provides a form view to edit permission requests, but permissions may also be requested using an AJAX POST request.
    """
    model = models.UserPermissionLink
    form_class = forms.PermissionRequestForm
    template_name = 'datasources/user_permission_link/form.html'

    def get_context_data(self, **kwargs):
        """
        Add data source to the context.
        """
        context = super().get_context_data()

        context['datasource'] = models.DataSource.objects.get(pk=self.kwargs['pk'])

        return context

    def get_object(self, queryset=None):
        """
        Get or create a permission object for the relevant user.
        """
        self.datasource = models.DataSource.objects.get(pk=self.kwargs['pk'])
        user = self.request.user

        if self.request.user == self.datasource.owner or self.request.user.is_superuser:
            try:
                # Let owner and admins edit other user's requests
                user = get_user_model().objects.get(id=self.request.GET.get('user'))

            except ObjectDoesNotExist:
                pass

        obj, created = self.model.objects.get_or_create(
            user=user,
            datasource=self.datasource
        )

        return obj

    def form_valid(self, form):
        """
        Automatically grant requests which are either:
            - Edited by owner / admin
            - Requests for a reduction in permission level
        """
        if (
                self.request.user == self.datasource.owner or self.request.user.is_superuser or
                form.instance.granted > form.instance.requested
        ):
            form.instance.granted = form.instance.requested

        return super().form_valid(form)

    def get_success_url(self):
        """
        Return to the data source or access management view depending on user class.
        """
        if self.request.user == self.datasource.owner or self.request.user.is_superuser:
            return reverse('datasources:datasource.access.manage', kwargs={'pk': self.datasource.pl})

        return reverse('datasources:datasource.detail', kwargs={'pk': self.datasource.pk})


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
