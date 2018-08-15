from django.conf import settings
from django.db import models
from django.urls import reverse


MAX_LENGTH_NAME = 63


class Application(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    description = models.TextField(blank=True, null=False)

    url = models.URLField(blank=False, null=False)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.PROTECT,
                              related_name='applications',
                              blank=False, null=False)

    def get_absolute_url(self):
        return reverse('applications:application.detail',
                       kwargs={'pk': self.pk})
