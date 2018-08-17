from django.conf import settings
from django.db import models
from django.urls import reverse


#: Length of CharFields used to hold the names of objects
MAX_LENGTH_NAME = 63


class Application(models.Model):
    """
    Manage the state of and access to an external application.

    An external application may be e.g.:

    * A data / metadata visualisation tool
    * A data / metadata analysis pipeline
    """
    #: Friendly name of this application
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    #: A brief description
    description = models.TextField(blank=True, null=False)

    #: Address at which the API may be accessed
    url = models.URLField(blank=False, null=False)

    #: User who has responsibility for this application
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              limit_choices_to={
                                  'groups__name': 'Application providers'
                              },
                              on_delete=models.PROTECT,
                              related_name='applications',
                              blank=False, null=False)

    def get_absolute_url(self):
        return reverse('applications:application.detail',
                       kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
