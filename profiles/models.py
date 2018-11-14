import enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from core.models import MAX_LENGTH_NAME


class Institution(models.Model):
    """
    Model representing the institution with which a user is associated.
    """
    @enum.unique
    class InstitutionType(enum.Enum):
        ACADEMIC = 'aca'
        BUSINESS = 'bus'
        CHARITY = 'cha'
        GOVERNMENT = 'gov'
        OTHER = 'oth'

        @classmethod
        def choices(cls):
            return tuple((i.value, i.name.title()) for i in cls)

    #: Name of the institution
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    #: Type of institution - e.g. academic, business, etc.
    type = models.CharField(max_length=3,
                            choices=InstitutionType.choices(),
                            blank=False, null=False)

    @property
    def auditors(self):
        return self.users.filter(is_auditor=True) + User.objects.filter(is_superauditor=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Model representing a user of PEDASI.
    """
    #: Institution to which this user belongs
    institution = models.ForeignKey(Institution, related_name='users',
                                    on_delete=models.SET_NULL,
                                    blank=True, null=True)

    #: Is this user an auditor of their institution?
    is_auditor = models.BooleanField(default=False,
                                     blank=False, null=False)

    #: Is this user a superauditor?  Superauditors are auditors across all of PEDASI
    is_superauditor = models.BooleanField(default=False,
                                          blank=False, null=False)

    def get_uri(self):
        """
        Get a URI for this user.

        Used in PROV records.
        """
        return reverse('profiles:uri', kwargs={'pk': self.pk})
