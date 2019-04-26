"""
This module contains the API endpoint viewset defining the PEDASI Application API.
"""

import csv
import json
import typing

from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import decorators, request, response, viewsets
from requests.exceptions import HTTPError

from .. import permissions
from datasources import models, serializers
from datasources.connectors.base import DatasetNotFoundError
from provenance import models as prov_models


class MetadataItemApiViewset(viewsets.ModelViewSet):
    """
    API ViewSet for viewing and managing dynamic metadata items on a data sources.
    """
    serializer_class = serializers.MetadataItemSerializer
    permission_classes = [permissions.IsOwnerOrReadOnly]

    def get_datasource(self):
        return get_object_or_404(models.DataSource, pk=self.kwargs['datasource_pk'])

    def get_queryset(self):
        return models.MetadataItem.objects.filter(datasource=self.kwargs['datasource_pk'])

    def perform_create(self, serializer):
        serializer.save(datasource=self.get_datasource())


class DataSourceApiViewset(viewsets.ReadOnlyModelViewSet):
    """
    Provides views for:

    /api/datasources/
      List all :class:`datasources.models.DataSource`\ s.

    /api/datasources/<int>/
      Retrieve a single :class:`datasources.models.DataSource`.

    /api/datasources/<int>/quality/
      Get the quality level of a :class:`datasources.models.DataSource` using the current ruleset.

    /api/datasources/<int>/prov/
      Retrieve PROV records related to a :class:`datasources.models.DataSource`.

    /api/datasources/<int>/metadata/
      Retrieve :class:`datasources.models.DataSource` metadata via API call to data source URL.

    /api/datasources/<int>/data/
      Retrieve :class:`datasources.models.DataSource` data via API call to data source URL.

    /api/datasources/<int>/datasets/
      Retrieve :class:`datasources.models.DataSource` list of data sets via API call to data source URL.

    /api/datasources/<int>/datasets/<href>/metadata/
      Retrieve :class:`datasources.models.DataSource` metadata for a single dataset via API call to data source URL.

    /api/datasources/<int>/datasets/<href>/metadata/
      Retrieve :class:`datasources.models.DataSource` data for a single dataset via API call to data source URL.
    """
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceSerializer
    permission_classes = [permissions.ViewPermission]

    def _create_prov_entry(self, instance: models.DataSource) -> None:
        """
        Create a PROV entry linking the data source and the authenticated user.
        """
        # TODO should PROV distinguish between data and metadata accesses?
        # TODO should we create PROV records for requests that failed

        try:
            # Is the user actually a proxy for an application?
            application = self.request.user.application_proxy

            prov_models.ProvWrapper.create_prov(
                instance,
                self.request.user.get_uri(),
                application=application,
                activity_type=prov_models.ProvActivity.ACCESS
            )

        except ObjectDoesNotExist:
            # Normal (non-proxy) user
            prov_models.ProvWrapper.create_prov(
                instance,
                self.request.user.get_uri(),
                activity_type=prov_models.ProvActivity.ACCESS
            )

        except AttributeError:
            # No logged in user - but has passed permission checks - data source must be public
            pass

    def _filter_by_metadata(self, queryset):
        """
        Query filter to filter data sources by variable metadata.

        Query parameters are key value pairs of the metadata field short name and the metadata value.

        :return: Filtered queryset
        """
        for key, value in self.request.query_params.items():
            # The key 'search' is used to activate filters.SearchFilter - don't interfere with it
            if key == 'search':
                continue

            queryset = queryset.filter(metadata_items__field__short_name=key,
                                       metadata_items__value=value)

        return queryset

    def try_passthrough_response(self,
                                 map_response: typing.Callable[..., HttpResponse],
                                 error_message: str,
                                 dataset: str = None) -> HttpResponse:
        """
        Attempt to pass a response from the data connector using the function `map_response`.

        If the data connectors raises an error (AttributeError, DatasetNotFoundError or NotImplementedError)
        then return an error response.

        :param map_response: Function to get response from data connector - must return HttpResponse
        :param error_message: Error message in case data connector raises an error
        :param dataset: Dataset to access within data source
        :return: HttpResponse from data connector or error response
        """
        instance = self.get_object()

        with instance.data_connector as data_connector:
            # Are there any query params to pass on?
            params = self.request.query_params
            if not params:
                params = None

            if dataset is not None:
                try:
                    data_connector = data_connector[dataset]

                except DatasetNotFoundError:
                    data = {
                        'status': 'error',
                        'message': 'Dataset does not exist within this data source'
                    }
                    return response.Response(data, status=404)

            # Record this action in PROV
            if not instance.prov_exempt:
                self._create_prov_entry(instance)

            try:
                return map_response(data_connector, params)

            except (AttributeError, NotImplementedError):
                data = {
                    'status': 'error',
                    'message': error_message,
                }
                return response.Response(data, status=400)

            except HTTPError as e:
                # Pass upstream errors through
                return response.Response(e.response.text, status=e.response.status_code)

    def list(self, request, *args, **kwargs):
        """
        List the queryset after filtering by request query parameters for data source metadata.
        """
        queryset = self._filter_by_metadata(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=True, permission_classes=[permissions.ViewPermission])
    def quality(self, request, pk=None):
        """
        View for /api/datasources/<int>/quality/

        Get the quality level of a data source using the current ruleset.
        """
        ruleset = get_user_model().get_quality_ruleset()
        instance = self.get_object()

        return response.Response({
            'quality': ruleset(instance),
        }, status=200)

    @decorators.action(detail=True, permission_classes=[permissions.ProvPermission], name='datasource-quality')
    def prov(self, request, pk=None):
        """
        View for /api/datasources/<int>/prov/

        Retrieve PROV records related to a :class:`DataSource`.
        """
        instance = self.get_object()

        data = {
            # Get all ProvEntry's related to this instance and encode them as JSON
            'prov': [json.loads(record.to_json()) for record in prov_models.ProvWrapper.filter_model_instance(instance)]
        }

        # Record this action in PROV
        if not instance.prov_exempt:
            self._create_prov_entry(instance)

        return response.Response(data, status=200)

    @decorators.action(detail=True, permission_classes=[permissions.MetadataPermission])
    def metadata(self, request, pk=None):
        """
        View for /api/datasources/<int>/metadata/

        Retrieve :class:`DataSource` metadata via API call to data source URL.
        """
        def map_response(data_connector, params):
            data = {
                'status': 'success',
                'data': data_connector.get_metadata(params=params)
            }
            return response.Response(data, status=200)

        return self.try_passthrough_response(map_response,
                                             'Data source does not provide metadata')

    @decorators.action(detail=True, methods=['GET'],
                       permission_classes=[permissions.DataPermission, permissions.DataPushPermission])
    def data(self, request, pk=None):
        """
        View for /api/datasources/<int>/data/

        Retrieve :class:`DataSource` data via API call to data source URL.
        """
        def map_response(data_connector, params):
            r = data_connector.get_response(params=params)
            try:
                return HttpResponse(r.text, status=r.status_code,
                                    content_type=r.headers.get('content-type'))

            except AttributeError:
                # Should be a Django response already
                return r

        return self.try_passthrough_response(map_response,
                                             'Data source does not provide data')

    @data.mapping.post
    def post_data(self, request: request.Request, pk=None):
        """
        Add data to this data source.  Only applicable to internal data sources.

        Data can be added either as JSON body text or as a POSTed CSV file.
        """
        instance = self.get_object()

        try:
            with instance.data_connector as data_connector:
                if request.FILES:
                    for filename, f in request.FILES.items():
                        # TODO read in chunks
                        # TODO don't assume utf-8
                        data = f.read().decode('utf-8').splitlines()
                        reader = csv.DictReader(data)

                        data_connector.post_data(reader)

                else:
                    data_connector.post_data(request.data)

                # Rebuild index
                index_fields = instance.metadata_items.filter(field__short_name='indexed_field').values_list('value')
                if index_fields:
                    data_connector.clean_data(index_fields=index_fields)

                # Record this action in PROV
                if not instance.prov_exempt:
                    self._create_prov_entry(instance)

        except AttributeError:
            # Connector has no 'post_data' method
            return JsonResponse({
                'status': 'error',
                'message': 'Data source does not support writing of data'
            }, status=405)

        return JsonResponse({
            'status': 'success',
            'data': None,
        })

    @data.mapping.put
    def put_data(self, request: request.Request, pk=None):
        instance = self.get_object()

        with instance.data_connector as data_connector:
            # Remove all existing data
            data_connector.clear_data()

        return self.post_data(request, pk)

    @decorators.action(detail=True, permission_classes=[permissions.MetadataPermission])
    def datasets(self, request, pk=None):
        """
        View for /api/datasources/<int>/datasets/

        Retrieve :class:`DataSource` list of data sets via API call to data source URL.
        """
        def map_response(data_connector, params):
            data = {
                'status': 'success',
                'data': data_connector.get_datasets(params=params)
            }
            return response.Response(data, status=200)

        return self.try_passthrough_response(map_response,
                                             'Data source does not contain datasets')

    # TODO URL pattern here uses pre Django 2 format
    @decorators.action(detail=True,
                       url_path='datasets/(?P<href>.*)/metadata',
                       permission_classes=[permissions.MetadataPermission])
    def dataset_metadata(self, request, pk=None, **kwargs):
        """
        View for /api/datasources/<int>/datasets/<href>/metadata/

        Retrieve :class:`DataSource` metadata for a single dataset via API call to data source URL.
        """
        def map_response(data_connector, params):
            data = {
                'status': 'success',
                'data': data_connector.get_metadata(params=params)
            }
            return response.Response(data, status=200)

        return self.try_passthrough_response(map_response,
                                             'Data source does not provide metadata',
                                             dataset=self.kwargs['href'])

    # TODO URL pattern here uses pre Django 2 format
    @decorators.action(detail=True,
                       url_path='datasets/(?P<href>.*)/data',
                       permission_classes=[permissions.DataPermission])
    def dataset_data(self, request, pk=None, **kwargs):
        """
        View for /api/datasources/<int>/datasets/<href>/data/

        Retrieve :class:`DataSource` data for a single dataset via API call to data source URL.
        """
        def map_response(data_connector, params):
            r = data_connector.get_response(params=params)
            return HttpResponse(r.text, status=r.status_code,
                                content_type=r.headers.get('content-type'))

        return self.try_passthrough_response(map_response,
                                             'Data source does not provide data',
                                             dataset=self.kwargs['href'])
