import json

from rest_framework import serializers

from . import models
from provenance import models as prov_models


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataSource
        fields = ['name', 'description', 'url']
