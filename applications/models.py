from django.conf import settings
from django.db import models
from django.urls import reverse

from pedasi.common.base_models import BaseAppDataModel


class Application(BaseAppDataModel):
    """
    Manage the state of and access to an external application.

    An external application may be e.g.:

    * A data / metadata visualisation tool
    * A data / metadata analysis pipeline
    """
    #: User who has responsibility for this application
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              limit_choices_to={
                                  'groups__name': 'Application providers'
                              },
                              on_delete=models.PROTECT,
                              related_name='applications',
                              editable=False,
                              blank=False, null=False)

    def get_absolute_url(self):
        return reverse('applications:application.detail',
                       kwargs={'pk': self.pk})

