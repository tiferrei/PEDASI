import contextlib
import enum
import json
import typing

from django.conf import settings
from django.contrib.auth.models import Group
from django.core import validators
from django.db import models
from django.urls import reverse
import requests
import requests.exceptions

from core.models import BaseAppDataModel, MAX_LENGTH_API_KEY, MAX_LENGTH_NAME, MAX_LENGTH_PATH
from datasources.connectors.base import AuthMethod, BaseDataConnector, REQUEST_AUTH_FUNCTIONS

#: Length of request reason field - must include brief description of project
MAX_LENGTH_REASON = 511


class MetadataField(models.Model):
    """
    A metadata field that can be dynamically added to a data source.
    """
    #: Name of the field
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            unique=True,
                            blank=False, null=False)

    short_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                  validators=[
                                      validators.RegexValidator(
                                          '^[a-zA-Z][a-zA-Z0-9_]*\Z',
                                          'Short name must begin with a letter and consist only of letters, numbers and underscores.',
                                          'invalid'
                                      )
                                  ],
                                  unique=True,
                                  blank=False, null=False)

    def __str__(self):
        return self.name


class MetadataItem(models.Model):
    """
    The value of the metadata field on a given data source.
    """
    #: The value of this metadata field
    value = models.CharField(max_length=MAX_LENGTH_REASON,
                             blank=True, null=False)

    #: To which field does this relate?
    field = models.ForeignKey(MetadataField,
                              related_name='values',
                              on_delete=models.PROTECT,
                              blank=False, null=False)

    #: To which data source does this relate?
    datasource = models.ForeignKey('DataSource',
                                   related_name='metadata_items',
                                   on_delete=models.CASCADE,
                                   blank=False, null=False)

    class Meta:
        unique_together = (('field', 'datasource', 'value'),)

    def __str__(self):
        return self.value


@enum.unique
class UserPermissionLevels(enum.IntEnum):
    """
    User permission levels on data sources.
    """
    #: No permissions
    NONE = 0

    #: Permission to view in PEDASI UI
    VIEW = 1

    #: Permission to query metadata via API / UI
    META = 2

    #: Permission to query data via API / UI
    DATA = 3

    #: Permission to query PROV via API / UI
    PROV = 4

    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)


class UserPermissionLink(models.Model):
    """
    Model to act as a many to many joining table to handle user permission levels for access to data sources.
    """
    #: User being managed
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    #: Data source on which the permissions are being granted
    datasource = models.ForeignKey('DataSource',
                                   on_delete=models.CASCADE)

    #: Granted permission level
    granted = models.IntegerField(choices=UserPermissionLevels.choices(),
                                  default=UserPermissionLevels.NONE,
                                  blank=False, null=False)

    #: Requested permission level
    requested = models.IntegerField(choices=UserPermissionLevels.choices(),
                                    default=UserPermissionLevels.NONE,
                                    blank=False, null=False)

    #: Reason the permission was requested
    reason = models.CharField(max_length=MAX_LENGTH_REASON,
                              blank=True, null=False)


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

    #: Contains encrypted data?
    is_encrypted = models.BooleanField(default=False,
                                       blank=False, null=False)

    #: Where to find information about how to use this encrypted data
    encrypted_docs_url = models.URLField('Documentation URL for managing encrypted data',
                                         blank=True, null=False)

    #: Which authentication method to use - defined in :class:`datasources.connectors.base.AuthMethod` enum
    auth_method = models.IntegerField(choices=AuthMethod.choices(),
                                      default=AuthMethod.UNKNOWN,
                                      blank=False, null=False)

    #: Users - linked via a permission table - see :class:`UserPermissionLink`
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   through=UserPermissionLink)

    #: The level of access that users are assumed to have without gaining explicit permission
    public_permission_level = models.IntegerField(choices=UserPermissionLevels.choices(),
                                                  default=UserPermissionLevels.DATA.value,
                                                  blank=False, null=False)

    #: Is this data source exempt from PROV tracking - e.g. utility data sources - postcode lookup
    prov_exempt = models.BooleanField(default=False,
                                      help_text=(
                                          'Should this data source be exempt from PROV tracking? '
                                          'This is useful for utility data sources which expect a large volume '
                                          'of queries, but are not interested in analysing usage patterns. '
                                          'Note that this only disables tracking of data accesses, '
                                          'not of updates to the data source in PEDASI.'
                                      ),
                                      blank=False, null=False)

    #: Total number of requests sent to the external API
    external_requests_total = models.PositiveIntegerField(default=0,
                                                          editable=False, blank=False, null=False)

    #: Number of requests sent to the external API since the last reset - reset at midnight by cron job
    external_requests = models.PositiveIntegerField(default=0,
                                                    editable=False, blank=False, null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_connector = None

    def has_view_permission(self, user: settings.AUTH_USER_MODEL) -> bool:
        """
        Does a user have permission to view this data source in the PEDASI UI?

        :param user: User to check
        :return: User has permission?
        """
        return self.has_permission_level(user, UserPermissionLevels.VIEW)

    def has_permission_level(self, user: settings.AUTH_USER_MODEL, level: UserPermissionLevels) -> bool:
        """
        Does a user have a particular permission level on this data source?

        :param user: User to check
        :param level: Permission level to check for
        :return: User has permission?
        """
        if self.public_permission_level >= level:
            # Everyone has access
            return True

        if self.owner == user or user.is_superuser:
            return True

        try:
            permission = UserPermissionLink.objects.get(
                user=user,
                datasource=self
            )
        except (UserPermissionLink.DoesNotExist, TypeError):
            # TypeError - user is not logged in
            return False

        return permission.granted >= level

    def has_edit_permission(self, user: settings.AUTH_USER_MODEL) -> bool:
        """
        Does a given user have permission to edit this data source?

        :param user: User to check
        :return: User has permission to edit?
        """
        return user.is_superuser or user == self.owner

    @property
    def is_catalogue(self) -> bool:
        return self.data_connector_class.is_catalogue

    @property
    def connector_string(self):
        if self._connector_string:
            return self._connector_string
        return self.url

    @property
    def data_connector_class(self) -> typing.Type[BaseDataConnector]:
        """
        Get the data connector class for this source.

        :return: Data connector class
        """
        BaseDataConnector.load_plugins('datasources/connectors')

        try:
            plugin = BaseDataConnector.get_plugin(self.plugin_name)

        except KeyError as e:
            if not self.plugin_name:
                raise ValueError('Data source plugin is not set') from e

            raise KeyError('Data source plugin not found') from e

        return plugin

    @property
    @contextlib.contextmanager
    def data_connector(self) -> BaseDataConnector:
        """
        Context manager to construct the data connector for this source.

        :return: Data connector instance
        """
        if self._data_connector is None:
            plugin = self.data_connector_class

            if not self.api_key:
                self._data_connector = plugin(self.connector_string)

            else:
                # Is the authentication method set?
                auth_method = AuthMethod(self.auth_method)
                if not auth_method:
                    auth_method = self.determine_auth_method(self.url, self.api_key)

                # Inject function to get authenticated request
                auth_class = REQUEST_AUTH_FUNCTIONS[auth_method]

                self._data_connector = plugin(self.connector_string, self.api_key,
                                              auth=auth_class)

        try:
            # Returns as context manager
            yield self._data_connector

        finally:
            # Executed after the context manager is closed
            self.external_requests += self._data_connector.request_count
            self.external_requests_total += self._data_connector.request_count

            self.save()

    @property
    def search_representation(self) -> str:
        lines = [
            self.name,
            self.owner.get_full_name(),
            self.description,
        ]

        try:
            lines.append(json.dumps(
                self.data_connector.get_metadata(),
                indent=4
            ))

        except:
            # KeyError: Plugin was not found
            # NotImplementedError: Plugin does not support metadata
            # ValueError: Plugin was not set
            pass

        result = '\n'.join(lines)
        return result

    @staticmethod
    def determine_auth_method(url: str, api_key: str) -> AuthMethod:
        # If not using an API key - can't require auth
        if not api_key:
            return AuthMethod.NONE

        for auth_method_id, auth_function in REQUEST_AUTH_FUNCTIONS.items():
            try:
                # Can we get a response using this auth method?
                if auth_function is None:
                    response = requests.get(url)

                else:
                    response = requests.get(url,
                                            auth=auth_function(api_key, ''))

                response.raise_for_status()
                return auth_method_id

            except requests.exceptions.HTTPError:
                pass

        # None of the attempted authentication methods was successful
        raise requests.exceptions.ConnectionError('Could not authenticate against external API')

    def get_absolute_url(self):
        return reverse('datasources:datasource.detail',
                       kwargs={'pk': self.pk})
