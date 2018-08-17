from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom Django user model to allow for additional functionality to be
    added more easily in the future.
    """
    pass
