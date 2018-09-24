from rest_framework import serializers

from . import models


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataSource
        fields = ('name', 'description', 'url')
