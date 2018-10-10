from rest_framework import decorators, generics, renderers, response, viewsets

from datasources import models, serializers


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


# Has to be a viewset so we can add it to a router
class DataSourceMetadataApiView(generics.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    View for /api/datasources/<int>/metadata/

    Retrieves :class:`DataSource` metadata via API call to data source URL.
    """
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceMetadataSerializer

    # TODO consider moving this into DataSourceApiViewset
    # Decorator adds this as a 'metadata/' URL on the end of the existing URL path
    @decorators.action(detail=True)
    def metadata(self, request, pk=None):
        return self.retrieve(request, pk)

    def get_serializer_context(self):
        """
        Pass query params on to Serializer to use in API query.
        """
        context = super().get_serializer_context()

        context['params'] = self.request.query_params

        return context


# Has to be a viewset so we can add it to a router
class DataSourceDataApiView(generics.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    View for /api/datasources/<int>/data/

    Retrieves :class:`DataSource` data via API call to data source URL.
    """
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceDataSerializer

    # TODO consider moving this into DataSourceApiViewset
    # Decorator adds this as a 'data/' URL on the end of the existing URL path
    @decorators.action(detail=True)
    def data(self, request, pk=None):
        return self.retrieve(request, pk)

    def get_serializer_context(self):
        """
        Pass query params on to Serializer to use in API query.
        """
        context = super().get_serializer_context()

        context['params'] = self.request.query_params

        return context


# Has to be a viewset so we can add it to a router
class DataSourceDataSetsListApiView(generics.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    View for /api/datasources/<int>/datasets/

    Retrieves :class:`DataSource` list of data sets via API call to data source URL.
    """
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceDataSetsSerializer

    # TODO consider moving this into DataSourceApiViewset
    # Decorator adds this as a 'datasets/' URL on the end of the existing URL path
    @decorators.action(detail=True)
    def datasets(self, request, pk=None):
        # return self.retrieve(request, pk)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    def get_serializer_context(self):
        """
        Pass query params on to Serializer to use in API query.
        """
        context = super().get_serializer_context()

        context['params'] = self.request.query_params

        return context


# Has to be a viewset so we can add it to a router
class DataSourceDatasetMetadataApiView(generics.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    View for /api/datasources/<int>/datasets/<href>/metadata/

    Retrieves :class:`DataSource` metadata for a single dataset via API call to data source URL.
    """
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceDatasetMetadataSerializer

    # TODO consider moving this into DataSourceApiViewset
    # Decorator adds this as a 'metadata/' URL on the end of the existing URL path
    @decorators.action(detail=True)
    def metadata(self, request, pk=None, **kwargs):
        return self.retrieve(request, pk)

    def get_serializer_context(self):
        """
        Pass query params on to Serializer to use in API query.
        """
        context = super().get_serializer_context()

        context['href'] = self.kwargs['href']
        context['params'] = self.request.query_params

        return context


class PassthroughRenderer(renderers.BaseRenderer):
    """
    Django-rest-api renderer which passes data without transformation.
    """
    # This media type seems to most strongly imply that the true type depends on the proxied request
    media_type = 'multipart/related'
    format = 'passthrough'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        try:
            return data.encode(self.charset)
        except AttributeError:
            # OPTIONS request must be handled using JSONRenderer
            renderer = renderers.JSONRenderer()
            return renderer.render(data, 'application/json', renderer_context)


# Has to be a viewset so we can add it to a router
class DataSourceDatasetDataApiView(generics.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    View for /api/datasources/<int>/datasets/<href>/metadata/

    Retrieves :class:`DataSource` data for a single dataset via API call to data source URL.
    """
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceDatasetDataSerializer
    renderer_classes = [renderers.BrowsableAPIRenderer, PassthroughRenderer]

    # TODO consider moving this into DataSourceApiViewset
    # Decorator adds this as a 'data/' URL on the end of the existing URL path
    @decorators.action(detail=True)
    def data(self, request, pk=None, **kwargs):
        instance = self.get_object()

        data_connector = instance.data_connector
        self._response = data_connector.get_data_passthrough(
            dataset=self.kwargs['href'],
            params=self.request.query_params
        )

        return response.Response(self._response.text)
