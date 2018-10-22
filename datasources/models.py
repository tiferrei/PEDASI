import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse

from datasources.connectors.base import BaseDataConnector
from core.models import BaseAppDataModel, MAX_LENGTH_API_KEY, MAX_LENGTH_NAME


class DataSource(BaseAppDataModel):
    """
    Manage access to a data source API.

    Will provide functionality to:

    * Query data (with query params)
    * Query metadata (with query params)
    * Track provenance of the data source itself
    * Track provenance of data accesses
    """
    #: User who has responsibility for this data source
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              limit_choices_to={
                                  'groups__name': 'Data providers'
                              },
                              on_delete=models.PROTECT,
                              related_name='datasources',
                              blank=False, null=False)

    #: Name of plugin which allows interaction with this data source
    plugin_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                   blank=False, null=False)

    #: If the data source API requires an API key use this one
    api_key = models.CharField(max_length=MAX_LENGTH_API_KEY,
                               blank=True, null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_connector = None

    @property
    def data_connector(self):
        if self._data_connector is None:
            BaseDataConnector.load_plugins('datasources/connectors')
            plugin = BaseDataConnector.get_plugin(self.plugin_name)

            if self.api_key:
                self._data_connector = plugin(self.url, self.api_key)
            else:
                self._data_connector = plugin(self.url)

        return self._data_connector

    @property
    def search_representation(self):
        lines = []

        lines.append(self.name)
        lines.append(self.owner.get_full_name())
        lines.append(self.description)

        try:
            lines.append(json.dumps(
                self.data_connector.get_metadata(),
                indent=4
            ))
        except NotImplementedError:
            pass

        result = '\n'.join(lines)
        print(result)
        return result

    def get_absolute_url(self):
        return reverse('datasources:datasource.detail',
                       kwargs={'pk': self.pk})
