from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse


#: Length of CharFields used to hold the names of objects
MAX_LENGTH_NAME = 63


class DataSource(models.Model):
    """
    Manage access to a data source API.

    Will provide functionality to:

    * Query data (with query params)
    * Query metadata (with query params)
    * Track provenance of the data source itself
    * Track provenance of data accesses
    """
    #: Friendly name of this data source
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    #: A brief description
    description = models.TextField(blank=True, null=False)

    #: Address at which the API may be accessed
    url = models.URLField(blank=False, null=False)

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
                                    blank=True, null=True)

    #: Groups of users who have requested explicit permission to use this data source
    users_group_requested = models.ForeignKey(Group,
                                              on_delete=models.SET_NULL,
                                              related_name='datasource_requested',
                                              blank=True, null=True)

    #: Do users require explicit permission to use this data source?
    access_control = models.BooleanField(default=False,
                                         blank=False, null=False)

    def has_permission(self, user: settings.AUTH_USER_MODEL) -> bool:
        """
        Does a user have permission to use this data source?

        :param user: User to check
        :return: User has permission?
        """
        if not self.access_control:
            return True

        return user.groups.exists(self.users_group)

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

    def __str__(self):
        return self.name
