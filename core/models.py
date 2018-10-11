import abc

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models


#: Length of CharFields used to hold the names of objects
MAX_LENGTH_NAME = 63

MAX_LENGTH_API_KEY = 127


class BaseAppDataModel(models.Model):
    #: Friendly name of this application
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    #: A brief description
    description = models.TextField(blank=True, null=False)

    #: Address at which the API may be accessed
    url = models.URLField(blank=False, null=False)

    #: Do users require explicit permission to use this data source / application?
    access_control = models.BooleanField(default=False,
                                         blank=False, null=False)

    # TODO replace this with an admin group
    @property
    @abc.abstractmethod
    def owner(self):
        """
        User responsible for this data source / application.
        """
        raise NotImplementedError

    #: Group of users who have read / use access to this data source / application
    users_group = models.OneToOneField(Group,
                                       on_delete=models.SET_NULL,
                                       related_name='+',
                                       editable=False,
                                       blank=True, null=True)

    #: Groups of users who have requested access to this data source / application
    users_group_requested = models.OneToOneField(Group,
                                                 on_delete=models.SET_NULL,
                                                 related_name='+',
                                                 editable=False,
                                                 blank=True, null=True)

    @property
    def _access_group_name(self):
        return str(type(self)) + ' ' + self.name + ' Users'

    def save(self, **kwargs):
        # Create access control groups if they do not exist
        # Make sure their names match self.name if they do exist
        if self.access_control:
            if self.users_group:
                # Update existing group name
                self.users_group.name = self._access_group_name
                self.users_group.save()

            else:
                self.users_group, created = Group.objects.get_or_create(
                    name=self._access_group_name
                )

            if self.users_group_requested:
                # Update existing group name
                self.users_group_requested.name = self._access_group_name + ' Requested'
                self.users_group_requested.save()

            else:
                self.users_group_requested, created = Group.objects.get_or_create(
                    name=self._access_group_name + ' Requested'
                )

        super().save(**kwargs)

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

    @abc.abstractmethod
    def get_absolute_url(self):
        raise NotImplementedError

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
