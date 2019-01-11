from django.contrib import messages
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
import requests.exceptions

from datasources import forms, models
from datasources.permissions import HasPermissionLevelMixin


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
        if context['has_edit_permission']:
            context['metadata_field_form'] = forms.MetadataFieldForm()

        try:
            context['is_catalogue'] = self.object.is_catalogue
        except (KeyError, ValueError):
            messages.error(self.request, 'This data source is not configured correctly.  Please notify the owner.')

        return context


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


class DataSourceMetadataAjaxView(APIView):
    model = models.DataSource

    class MetadataSerializer(serializers.ModelSerializer):
        class Meta:
            model = models.MetadataItem
            fields = '__all__'

    def get_object(self, pk):
        return self.model.objects.get(pk=pk)

    def post(self, request, pk, format=None):
        """
        Create a new MetadataItem associated with this DataSource.
        """
        datasource = self.get_object(pk)
        if 'datasource' not in request.data:
            request.data['datasource'] = datasource.pk

        serializer = self.MetadataSerializer(data=request.data)

        if serializer.is_valid():
            obj = serializer.save()

            return Response({
                'status': 'success',
                'data': {
                    'datasource': datasource.pk,
                    'field': obj.field.name,
                    'field_short': obj.field.short_name,
                    'value': obj.value,
                }
            })

        return Response({'status': 'failure'}, status=400)

    def delete(self, request, pk, format=None):
        """
        Delete a MetadataItem associated with this DataSource.
        """
        datasource = self.get_object(pk)
        if 'datasource' not in request.data:
            request.data['datasource'] = datasource.pk

        metadata_item = models.MetadataItem.objects.get(
            datasource=datasource,
            field__short_name=self.request.data['field'],
            value=self.request.data['value']
        )

        metadata_item.delete()

        return Response({
            'status': 'success'
        })


class DataSourceExplorerView(HasPermissionLevelMixin, DetailView):
    model = models.DataSource
    template_name = 'datasources/datasource/explorer.html'
    context_object_name = 'datasource'

    permission_level = models.UserPermissionLevels.DATA

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['data_query_params'] = self.object.metadata_items.filter(
            field__short_name='data_query_param'
        ).values_list('value', flat=True)

        return context
