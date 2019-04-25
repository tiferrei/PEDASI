"""
This module contains the Django models necessary to manage the set of data sources.
"""

import contextlib
import enum
import json
import typing

from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import BaseAppDataModel, MAX_LENGTH_API_KEY, MAX_LENGTH_NAME, MAX_LENGTH_PATH, SoftDeletionManager
from datasources.connectors.base import AuthMethod, BaseDataConnector, REQUEST_AUTH_FUNCTIONS
from provenance.models import ProvAbleModel

#: Length of request reason field - must include brief description of project
MAX_LENGTH_REASON = 511


class Licence(models.Model):
    """
    Model representing a licence under which a data source is published e.g. Open Government Licence.
    """

    #: User who has responsibility for this licence
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              limit_choices_to={
                                  'groups__name': 'Data providers'
                              },
                              on_delete=models.PROTECT,
                              related_name='licences',
                              blank=False, null=False)

    #: Name of the licence - e.g. Open Government License
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    #: Short text identifier - e.g. OGL
    short_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                  blank=True, null=False)

    #: Licence version - e.g. v2.0
    version = models.CharField(max_length=MAX_LENGTH_NAME,
                               blank=False, null=False)

    #: Address at which the licence text may be accessed
    url = models.CharField(max_length=MAX_LENGTH_PATH,
                           blank=True, null=False)

    class Meta:
        unique_together = (('name', 'version'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('datasources:licence.detail', kwargs={'pk': self.pk})


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

    #: Have permission to push data?
    push_granted = models.BooleanField(default=False)

    #: Also require permission to push data?
    push_requested = models.BooleanField(default=False)

    #: Reason the permission was requested
    reason = models.CharField(max_length=MAX_LENGTH_REASON,
                              blank=True, null=False)

    class Meta:
        unique_together = (('user', 'datasource'),)


class DataSource(ProvAbleModel, BaseAppDataModel):
    """
    Manage access to a data source API.

    Will provide functionality to:

    * Query data (with query params)
    * Query metadata (with query params)
    * Track provenance of the data source itself
    * Track provenance of data accesses
    """
    objects = SoftDeletionManager()

    #: Address at which the API may be accessed
    url = models.CharField(max_length=MAX_LENGTH_PATH,
                           blank=True, null=False)

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
                                   default='DataSetConnector',
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

    #: Which licence is this data published under
    licence = models.ForeignKey(Licence,
                                related_name='datasources',
                                on_delete=models.PROTECT,
                                blank=True, null=True)

    #: Total number of requests sent to the external API
    external_requests_total = models.PositiveIntegerField(default=0,
                                                          editable=False, blank=False, null=False)

    #: Number of requests sent to the external API since the last reset - reset at midnight by cron job
    external_requests = models.PositiveIntegerField(default=0,
                                                    editable=False, blank=False, null=False)

    #: Has this object been soft deleted?
    is_deleted = models.BooleanField(default=False,
                                     editable=False, blank=False, null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_connector = None

    def save(self, *args, **kwargs):
        # TODO avoid determining auth method if existing one still works
        self.auth_method = self.data_connector_class.determine_auth_method(self.url, self.api_key)

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete this object.
        """
        self.is_deleted = True
        self.save()

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
        """
        Is this data source a data catalogue?
        """
        return self.data_connector_class.is_catalogue

    @property
    def connector_string(self):
        """
        Get the string used to locate the resource associated with this data source.

        e.g. URL, SQL table identifier, etc.
        """
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

        except KeyError as exc:
            if not self.plugin_name:
                raise ValueError('Data source plugin is not set') from exc

            raise KeyError('Data source plugin not found') from exc

        return plugin

    def _get_data_connector(self) -> BaseDataConnector:
        """
        Construct the data connector for this source.

        :return: Data connector instance
        """
        plugin = self.data_connector_class

        if not self.api_key:
            data_connector = plugin(self.connector_string)

        else:
            # Is the authentication method set?
            auth_method = AuthMethod(self.auth_method)
            if auth_method == AuthMethod.UNKNOWN:
                auth_method = plugin.determine_auth_method(self.url, self.api_key)

            # Inject function to get authenticated request
            auth_class = REQUEST_AUTH_FUNCTIONS[auth_method]

            data_connector = plugin(self.connector_string, self.api_key,
                                    auth=auth_class)

        return data_connector

    @property
    @contextlib.contextmanager
    def data_connector(self) -> BaseDataConnector:
        """
        Context manager to construct the data connector for this source.

        When the context manager is closed, the number of requests to the external API will be added to the total.

        :return: Data connector instance
        """
        if self._data_connector is None:
            self._data_connector = self._get_data_connector()

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
        """
        Provide a text representation of this data source to be entered into a search index.

        :return: Text representation of this data source
        """
        lines = [
            self.name,
            self.owner.get_full_name(),
            self.description,
        ]

        try:
            # Using the data_connector context manager results in an infinite recursion:
            #   1. Save data source
            #   2. Get search representation (this function)
            #   3. Close data connector context manager
            #   4. Save data source -> ...

            data_connector = self._get_data_connector()
            metadata = data_connector.get_metadata()

            lines.append(json.dumps(
                metadata,
                indent=4
            ))

        except (KeyError, NotImplementedError, ValueError):
            # KeyError: Plugin was not found
            # NotImplementedError: Plugin does not support metadata
            # ValueError: Plugin was not set
            pass

        result = '\n'.join(lines)
        return result

    def get_absolute_url(self):
        return reverse('datasources:datasource.detail',
                       kwargs={'pk': self.pk})
