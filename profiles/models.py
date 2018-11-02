from django.contrib.auth.models import AbstractUser
from django.urls import reverse


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
