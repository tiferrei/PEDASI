from collections import namedtuple

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
import requests.exceptions

from datasources import forms, models
from datasources.permissions import HasPermissionLevelMixin
from profiles.permissions import OwnerPermissionMixin


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

        context['has_edit_permission'] = self.request.user.is_superuser or self.request.user == self.object.owner

        try:
            context['is_catalogue'] = self.object.is_catalogue
        except (KeyError, ValueError):
            messages.error(self.request, 'This data source is not configured correctly.  Please notify the owner.')

        context['api_url'] = (
            'https://' if self.request.is_secure() else 'http://' +
            self.request.get_host() +
            '/api/datasources/{0}/'.format(self.object.pk)
        )

        return context


class DataSourceCreateView(PermissionRequiredMixin, CreateView):
    model = models.DataSource
    template_name = 'datasources/datasource/create.html'
    context_object_name = 'datasource'

    form_class = forms.DataSourceForm
    permission_required = 'datasources.add_datasource'

    def form_valid(self, form):
        try:
            owner = form.instance.owner

        except models.DataSource.owner.RelatedObjectDoesNotExist:
            form.instance.owner = self.request.user

        return super().form_valid(form)


class DataSourceUpdateView(OwnerPermissionMixin, UpdateView):
    model = models.DataSource
    template_name = 'datasources/datasource/update.html'
    context_object_name = 'datasource'

    form_class = forms.DataSourceForm
    permission_required = 'datasources.change_datasource'


class DataSourceDeleteView(OwnerPermissionMixin, DeleteView):
    model = models.DataSource
    template_name = 'datasources/datasource/delete.html'
    context_object_name = 'datasource'

    permission_required = 'datasources.delete_datasource'
    success_url = reverse_lazy('datasources:datasource.list')


class DataSourceDataSetSearchView(HasPermissionLevelMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/dataset_search.html'
    context_object_name = 'datasource'

    permission_level = models.UserPermissionLevels.META

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


FieldValueSet = namedtuple('FieldValueSet', ['field', 'list'])


class DataSourceMetadataView(OwnerPermissionMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/metadata.html'
    context_object_name = 'datasource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['ruleset'] = get_user_model().get_quality_ruleset()
        context['metadata_fields'] = models.MetadataField.objects.all()

        items = []
        present_fields = {item.field for item in self.object.metadata_items.all()}
        for field in present_fields:
            items.append(
                FieldValueSet(field, [
                    item for item in self.object.metadata_items.all() if item.field == field
                ])
            )
        context['metadata_items'] = items

        return context


class DataSourceExplorerView(HasPermissionLevelMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/explorer.html'
    context_object_name = 'datasource'

    permission_level = models.UserPermissionLevels.META

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['data_query_params'] = self.object.metadata_items.filter(
            field__short_name='data_query_param'
        ).values_list('value', flat=True)

        context['api_url'] = (
            'https://' if self.request.is_secure() else 'http://' +
                                                        self.request.get_host() +
                                                        '/api/datasources/{0}/'.format(self.object.pk)
        )

        return context
