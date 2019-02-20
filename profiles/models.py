"""
Module containing models required for user profiles.
"""
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from rest_framework.authtoken.models import Token


class User(AbstractUser):
    """
    Custom Django user model to allow for additional functionality to be
    added more easily in the future.
    """
    def get_uri(self):
        """
        Get a URI for this user.

        Used in PROV records.
        """
        return reverse('profiles:uri', kwargs={'pk': self.pk})

    def create_auth_token(self) -> Token:
        """
        Create an API auth token for this user.

        :return: API auth token instance
        """
        token, created = Token.objects.get_or_create(user=self)
        return token
