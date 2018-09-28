from rest_framework import viewsets

from datasources import models, serializers


class DataSourceApiViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceSerializer
