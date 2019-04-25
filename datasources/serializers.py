from rest_framework import serializers

from . import models


class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Licence
        fields = ['name', 'short_name', 'version', 'url']


class MetadataFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MetadataField
        fields = ['name', 'short_name']


class MetadataItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MetadataItem
        fields = ['field', 'value']


class DataSourceSerializer(serializers.ModelSerializer):
    metadata_items = MetadataItemSerializer(many=True, read_only=True)
    licence = LicenceSerializer(many=False, read_only=True)

    class Meta:
        model = models.DataSource
        fields = [
            'id',
            'name',
            'description',
            'url',
            'plugin_name',
            'licence',
            'is_encrypted',
            'encrypted_docs_url',
            'metadata_items'
        ]


class QualityCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QualityCriterion
        fields = ['weight', 'metadata_field']


class QualityLevelSerializer(serializers.ModelSerializer):
    criteria = QualityCriterionSerializer(many=True, read_only=True)

    class Meta:
        model = models.QualityLevel
        fields = ['level', 'threshold', 'criteria']


class QualityRulesetSerializer(serializers.ModelSerializer):
    levels = QualityLevelSerializer(many=True, read_only=True)

    class Meta:
        model = models.QualityRuleset
        fields = '__all__'
