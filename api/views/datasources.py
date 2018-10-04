from rest_framework import decorators, generics, viewsets

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
class DataSourceMetadataListApiView(generics.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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

