from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

import requests.exceptions

from datasources import models
from profiles.permissions import HasViewPermissionMixin
from provenance.models import ProvWrapper


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


class DataSourceAuditView(DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/audit.html'
    context_object_name = 'datasource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['records'] = ProvWrapper.filter_model_instance(self.object)

        return context
