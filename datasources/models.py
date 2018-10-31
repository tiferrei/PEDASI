import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
import requests
import requests.exceptions

from datasources.connectors.base import AuthMethod, BaseDataConnector, REQUEST_AUTH_FUNCTIONS
from core.models import BaseAppDataModel, MAX_LENGTH_API_KEY, MAX_LENGTH_NAME, MAX_LENGTH_PATH


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

    #: Information required to initialise the connector for this data source
    _connector_string = models.CharField(max_length=MAX_LENGTH_PATH,
                                         blank=True, null=False)

    #: Name of plugin which allows interaction with this data source
    plugin_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                   blank=False, null=False)

    #: If the data source API requires an API key use this one
    api_key = models.CharField(max_length=MAX_LENGTH_API_KEY,
                               blank=True, null=False)

    #: Which authentication method to use - defined in datasources.connectors.base.AuthMethod enum
    auth_method = models.IntegerField(choices=AuthMethod.choices(),
                                      default=AuthMethod.UNKNOWN.value,
                                      editable=False, blank=False, null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_connector = None

    def save(self, **kwargs):
        # Find out which auth method to use
        if not self.auth_method:
            self.auth_method = self._determine_auth().value

        return super().save(**kwargs)

    @property
    def connector_string(self):
        if self._connector_string:
            return self._connector_string
        return self.url

    @property
    def data_connector(self) -> BaseDataConnector:
        """
        Construct the data connector for this source.

        :return: Data connector instance
        """
        if self._data_connector is None:
            BaseDataConnector.load_plugins('datasources/connectors')

            try:
                plugin = BaseDataConnector.get_plugin(self.plugin_name)

            except KeyError as e:
                if not self.plugin_name:
                    raise ValueError('Data source plugin is not set') from e

                raise KeyError('Data source plugin not found') from e

            # Is the authentication method set?
            auth_method = AuthMethod(self.auth_method)
            if not auth_method:
                auth_method = self._determine_auth()

            # Inject function to get authenticated request
            auth_class = REQUEST_AUTH_FUNCTIONS[auth_method]

            if self.api_key:
                self._data_connector = plugin(self.connector_string, self.api_key,
                                              auth=auth_class)
            else:
                self._data_connector = plugin(self.connector_string,
                                              auth=auth_class)

        return self._data_connector

    @property
    def search_representation(self) -> str:
        lines = []

        lines.append(self.name)
        lines.append(self.owner.get_full_name())
        lines.append(self.description)

        try:
            lines.append(json.dumps(
                self.data_connector.get_metadata(),
                indent=4
            ))
        except (KeyError, NotImplementedError, ValueError):
            # KeyError: Plugin was not found
            # NotImplementedError: Plugin does not support metadata
            # ValueError: Plugin was not set
            pass

        result = '\n'.join(lines)
        return result

    def _determine_auth(self) -> AuthMethod:
        # If not using an API key - can't require auth
        if not self.api_key:
            return AuthMethod.NONE

        for auth_method_id, auth_function in REQUEST_AUTH_FUNCTIONS.items():
            try:
                # Can we get a response using this auth method?
                response = requests.get(self.url,
                                        auth=auth_function(self.api_key, ''))

                response.raise_for_status()
                return auth_method_id

            except (TypeError, requests.exceptions.HTTPError):
                pass

    def get_absolute_url(self):
        return reverse('datasources:datasource.detail',
                       kwargs={'pk': self.pk})
