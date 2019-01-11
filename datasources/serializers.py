from rest_framework import serializers

from . import models


class MetadataFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MetadataField
        fields = ['name', 'short_name']


class MetadataItemSerializer(serializers.ModelSerializer):
    field = MetadataFieldSerializer(read_only=True)

    class Meta:
        model = models.MetadataItem
        fields = ['field', 'value']


class DataSourceSerializer(serializers.ModelSerializer):
    metadata_items = MetadataItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.DataSource
        fields = [
            'id',
            'name',
            'description',
            'url',
            'plugin_name',
            'is_encrypted',
            'encrypted_docs_url',
            'public_permission_level',
            'prov_exempt',
            'metadata_items'
        ]
