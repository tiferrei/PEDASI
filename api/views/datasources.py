from rest_framework import decorators, generics, response, viewsets

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
    def metadata(self, request, pk=None):
        return self.retrieve(request, pk)

    def get_serializer_context(self):
        """
        Pass query params on to Serializer to use in API query.
        """
        context = super().get_serializer_context()

        context['href'] = self.kwargs['href']
        context['params'] = self.request.query_params

        return context
