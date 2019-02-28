from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from rest_framework.authtoken.models import Token

from core.models import BaseAppDataModel, SoftDeletionManager
from provenance.models import ProvAbleModel, ProvApplicationModel


class Application(ProvAbleModel, ProvApplicationModel, BaseAppDataModel):
    """
    Manage the state of and access to an external application.

    An external application may be e.g.:

    * A data / metadata visualisation tool
    * A data / metadata analysis pipeline
    """
    objects = SoftDeletionManager()

    #: Address at which the API may be accessed
    url = models.URLField(blank=True, null=False)

    #: User who has responsibility for this application
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              limit_choices_to={
                                  'groups__name': 'Application providers'
                              },
                              on_delete=models.PROTECT,
                              related_name='applications',
                              editable=False,
                              blank=False, null=False)

    #: Proxy user which this application will act as
    proxy_user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                      on_delete=models.PROTECT,
                                      related_name='application_proxy',
                                      editable=False,
                                      blank=True, null=True)

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

    #: Do users require explicit permission to use this application?
    access_control = models.BooleanField(default=False,
                                         blank=False, null=False)

    #: Has this object been soft deleted?
    is_deleted = models.BooleanField(default=False,
                                     editable=False, blank=False, null=False)

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete this object.
        """
        self.is_deleted = True
        self.save()

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

        if not self.proxy_user:
            self.proxy_user = self._get_proxy_user()

        super().save(**kwargs)

    def has_view_permission(self, user: settings.AUTH_USER_MODEL) -> bool:
        """
        Does a user have permission to use this application?

        :param user: User to check
        :return: User has permission?
        """
        if not self.access_control:
            return True
        if self.owner == user:
            return True

        return self.users_group.user_set.filter(pk=user.pk).exists()

    def _get_proxy_user(self) -> settings.AUTH_USER_MODEL:
        """
        Create a new proxy user for this application or return the existing one.

        :return: Instance of user model
        """
        if self.proxy_user:
            return self.proxy_user

        # Add random UUID to username to allow multiple applications with the same name
        proxy_username = 'application-proxy-' + slugify(self.name) + str(uuid4())
        proxy_user = get_user_model().objects.create_user(proxy_username)

        # Create an API access token for the proxy user
        proxy_user.create_auth_token()

        return proxy_user

    def get_absolute_url(self):
        return reverse('applications:application.detail',
                       kwargs={'pk': self.pk})

