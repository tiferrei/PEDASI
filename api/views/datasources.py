import json
import typing

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

    /api/datasources/<int>/prov/
      Retrieve PROV records related to a :class:`DataSource`

    /api/datasources/<int>/metadata/
      Retrieve :class:`DataSource` metadata via API call to data source URL

    /api/datasources/<int>/data/
      Retrieve :class:`DataSource` data via API call to data source URL

    /api/datasources/<int>/datasets/
      Retrieve :class:`DataSource` list of data sets via API call to data source URL

    /api/datasources/<int>/datasets/<href>/metadata/
      Retrieve :class:`DataSource` metadata for a single dataset via API call to data source URL

    /api/datasources/<int>/datasets/<href>/metadata/
      Retrieve :class:`DataSource` data for a single dataset via API call to data source URL
    """
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceSerializer

    def try_passthrough_response(self,
                                 map_response: typing.Callable[..., HttpResponse],
                                 error_message: str,
                                 dataset: str = None):
        instance = self.get_object()
        data_connector = instance.data_connector

        # Are there any query params to pass on?
        params = self.request.query_params
        if not params:
            params = None

        if dataset is not None:
            data_connector = data_connector[dataset]

        try:
            return map_response(data_connector, params)

        except NotImplementedError:
            data = {
                'status': 'error',
                'message': error_message,
            }
            return response.Response(data, status=400)

    @decorators.action(detail=True)
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
        return response.Response(data, status=200)

    @decorators.action(detail=True)
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

    @decorators.action(detail=True)
    def data(self, request, pk=None):
        """
        View for /api/datasources/<int>/data/

        Retrieve :class:`DataSource` data via API call to data source URL.
        """
        def map_response(data_connector, params):
            r = data_connector.get_response(params=params)
            return HttpResponse(r.text, status=r.status_code,
                                content_type=r.headers.get('content-type'))

        return self.try_passthrough_response(map_response,
                                             'Data source does not provide data')

    @decorators.action(detail=True)
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
                       url_path='datasets/(?P<href>.*)/metadata')
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
                       url_path='datasets/(?P<href>.*)/data')
    def dataset_data(self, request, pk=None, **kwargs):
        """
        View for /api/datasources/<int>/datasets/<href>/metadata/

        Retrieve :class:`DataSource` data for a single dataset via API call to data source URL.
        """
        def map_response(data_connector, params):
            r = data_connector.get_response(params=params)
            return HttpResponse(r.text, status=r.status_code,
                                content_type=r.headers.get('content-type'))

        return self.try_passthrough_response(map_response,
                                             'Data source does not provide data',
                                             dataset=self.kwargs['href'])
