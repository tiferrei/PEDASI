"""
This module contains models for functionality common to both Application and DataSource models.
"""

import abc

from django.db import models


#: Length of CharFields used to hold the names of objects
MAX_LENGTH_NAME = 63

MAX_LENGTH_API_KEY = 127

MAX_LENGTH_PATH = 255


class SoftDeletionManager(models.Manager):
    """
    Manager for soft-deletable objects.  Filters out objects which have `is_deleted` set.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseAppDataModel(models.Model):
    """
    The parent class of the Application and DataSource models - providing common functionality.

    This class is an abstract model and will not create a corresponding DB table.
    """
    #: Friendly name of this application
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    #: A brief description
    description = models.TextField(blank=True, null=False)

    # TODO replace this with an admin group
    @property
    @abc.abstractmethod
    def owner(self):
        """
        User responsible for this data source / application.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_absolute_url(self):
        """
        Return URL at which this object may be viewed.

        Method must be implemented by inheriting classes.
        """
        raise NotImplementedError

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
