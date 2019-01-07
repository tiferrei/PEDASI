import json
import typing

from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import decorators, response, viewsets

from .. import permissions
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

    def try_passthrough_response(self,
                                 map_response: typing.Callable[..., HttpResponse],
                                 error_message: str,
                                 dataset: str = None) -> HttpResponse:
        instance = self.get_object()

        with instance.data_connector as data_connector:
            # Are there any query params to pass on?
            params = self.request.query_params
            if not params:
                params = None

            if dataset is not None:
                data_connector = data_connector[dataset]

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

    @decorators.action(detail=True, permission_classes=[permissions.ProvPermission])
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

    @decorators.action(detail=True, permission_classes=[permissions.DataPermission])
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
