import json

from django.http import HttpResponse
from rest_framework import decorators, response, viewsets

from datasources import models, serializers
from provenance import models as prov_models


class DataSourceApiViewset(viewsets.ReadOnlyModelViewSet):
    """
    Provides views for:

    /api/datasources/
      List all :class:`DataSource`s

    /api/datasource/<int>/
      Retrieve a single :class:`DataSource`
    """
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceSerializer

    @decorators.action(detail=True)
    def prov(self, request, pk=None):
        """
        View for /api/datasources/<int>/prov/

        Retrieves PROV records related to a :class:`DataSource`.
        """
        instance = self.get_object()

        data = {
            # Get all ProvEntry's related to this instance and encode them as JSON
            'prov': [json.loads(record.to_json()) for record in prov_models.ProvWrapper.filter_model_instance(instance)]
        }
        return response.Response(data, status=200)

    @decorators.action(detail=True)
    def metadata(self, request, pk=None):
        """
        View for /api/datasources/<int>/metadata/

        Retrieves :class:`DataSource` metadata via API call to data source URL.
        """
        instance = self.get_object()
        data_connector = instance.data_connector

        # Are there any query params to pass on?
        params = self.request.query_params
        if not params:
            params = None

        try:
            data = {
                'status': 'success',
                'data': data_connector.get_metadata(params=params)
            }
            return response.Response(data, status=200)

        except NotImplementedError:
            data = {
                'status': 'error',
                'message': 'Data source does not provide metadata',
            }
            return response.Response(data, status=400)

    @decorators.action(detail=True)
    def data(self, request, pk=None):
        """
        View for /api/datasources/<int>/data/

        Retrieves :class:`DataSource` data via API call to data source URL.
        """
        instance = self.get_object()
        data_connector = instance.data_connector

        # Are there any query params to pass on?
        params = self.request.query_params
        if not params:
            params = None

        try:
            r = data_connector.get_data_passthrough(params=params)

            if 'json' in r.headers.get('content-type'):
                data = {
                    'status': 'success',
                    'data': r.json()
                }
                return response.Response(data, status=200)

            return HttpResponse(r.text, status=r.status_code,
                                content_type=r.headers.get('content-type'))

        except NotImplementedError:
            data = {
                'status': 'error',
                'message': 'Data source does not provide data',
            }
            return response.Response(data, status=400)

    @decorators.action(detail=True)
    def datasets(self, request, pk=None):
        """
        View for /api/datasources/<int>/datasets/

        Retrieves :class:`DataSource` list of data sets via API call to data source URL.
        """
        instance = self.get_object()
        data_connector = instance.data_connector

        # Are there any query params to pass on?
        params = self.request.query_params
        if not params:
            params = None

        try:
            data = {
                'status': 'success',
                'data': data_connector.get_datasets(params=params)
            }
            return response.Response(data, status=200)

        except NotImplementedError:
            data = {
                'status': 'error',
                'message': 'Data source does not contain datasets',
            }
            return response.Response(data, status=400)

    # TODO URL pattern here uses pre Django 2 format
    @decorators.action(detail=True,
                       url_path='datasets/(?P<href>.*)/metadata')
    def dataset_metadata(self, request, pk=None, **kwargs):
        """
        View for /api/datasources/<int>/datasets/<href>/metadata/

        Retrieves :class:`DataSource` metadata for a single dataset via API call to data source URL.
        """
        instance = self.get_object()
        data_connector = instance.data_connector

        # Are there any query params to pass on?
        params = self.request.query_params
        if not params:
            params = None

        data_connector = data_connector[kwargs['href']]

        try:
            data = {
                'status': 'success',
                'data': data_connector.get_metadata(params=params)
            }
            return response.Response(data, status=200)

        except NotImplementedError:
            data = {
                'status': 'error',
                'message': 'Data source does not provide metadata',
            }
            return response.Response(data, status=400)

    # TODO URL pattern here uses pre Django 2 format
    @decorators.action(detail=True,
                       url_path='datasets/(?P<href>.*)/data')
    def dataset_data(self, request, pk=None, **kwargs):
        """
        View for /api/datasources/<int>/datasets/<href>/metadata/

        Retrieves :class:`DataSource` data for a single dataset via API call to data source URL.
        """
        instance = self.get_object()
        data_connector = instance.data_connector

        # Are there any query params to pass on?
        params = self.request.query_params
        if not params:
            params = None

        data_connector = data_connector[kwargs['href']]

        try:
            r = data_connector.get_data_passthrough(params=params)

            if 'json' in r.headers.get('content-type'):
                data = {
                    'status': 'success',
                    'data': r.json()
                }
                return response.Response(data, status=200)

            return HttpResponse(r.text, status=r.status_code,
                                content_type=r.headers.get('content-type'))

        except NotImplementedError:
            data = {
                'status': 'error',
                'message': 'Data source does not provide data',
            }
            return response.Response(data, status=400)
