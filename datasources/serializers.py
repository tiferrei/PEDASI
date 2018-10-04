from rest_framework import serializers

from . import models


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataSource
        fields = ['name', 'description', 'url']


class DataSourceMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataSource
        fields = []

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['test'] = 'test repr'

        return rep