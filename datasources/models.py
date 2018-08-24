from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse

from datasources.connectors.base import BaseDataConnector
from pedasi.common.base_models import BaseAppDataModel, MAX_LENGTH_NAME


class DataSource(BaseAppDataModel):
    """
    Manage access to a data source API.

    Will provide functionality to:

    * Query data (with query params)
    * Query metadata (with query params)
    * Track provenance of the data source itself
    * Track provenance of data accesses
    """
    # TODO replace this with an admin group
    #: User who has responsibility for this data source
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              limit_choices_to={
                                  'groups__name': 'Data providers'
                              },
                              on_delete=models.PROTECT,
                              related_name='datasources',
                              blank=False, null=False)

    #: Group of users who have explicit permission to use (query) this data source
    users_group = models.ForeignKey(Group,
                                    on_delete=models.SET_NULL,
                                    related_name='datasource',
                                    editable=False,
                                    blank=True, null=True)

    #: Groups of users who have requested explicit permission to use this data source
    users_group_requested = models.ForeignKey(Group,
                                              on_delete=models.SET_NULL,
                                              related_name='datasource_requested',
                                              editable=False,
                                              blank=True, null=True)

    #: Do users require explicit permission to use this data source?
    access_control = models.BooleanField(default=False,
                                         blank=False, null=False)

    #: Name of plugin which allows interaction with this data source
    plugin_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                   blank=False, null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_connector = None

    @property
    def data_connector(self):
        if self._data_connector is None:
            BaseDataConnector.load_plugins('datasources/connectors')
            plugin = BaseDataConnector.get_plugin(self.plugin_name)
            self._data_connector = plugin(self.url)

        return self._data_connector

    def has_view_permission(self, user: settings.AUTH_USER_MODEL) -> bool:
        """
        Does a user have permission to use this data source?

        :param user: User to check
        :return: User has permission?
        """
        if not self.access_control:
            return True
        if self.owner == user:
            return True

        return self.users_group.user_set.filter(pk=user.pk).exists()

    def save(self, **kwargs):
        if self.access_control:
            # Create access control groups if they do not exist
            self.users_group, created = Group.objects.get_or_create(
                name=self.name + ' Users'
            )
            self.users_group_requested, created = Group.objects.get_or_create(
                name=self.name + ' Users Requested'
            )

        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse('datasources:datasource.detail',
                       kwargs={'pk': self.pk})
