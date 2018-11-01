from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from rest_framework.authtoken.models import Token

from core.models import BaseAppDataModel


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

    #: Proxy user which this application will act as
    proxy_user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                      on_delete=models.PROTECT,
                                      related_name='application_proxy',
                                      editable=False,
                                      blank=True, null=True)

    def _get_proxy_user(self) -> settings.AUTH_USER_MODEL:
        """
        Create a new proxy user for this application or return the existing one.

        :return: Instance of user model
        """
        if self.proxy_user:
            return self.proxy_user

        proxy_username = 'application-proxy-' + slugify(self.name)
        proxy_user = get_user_model().objects.create_user(proxy_username)

        # Create an API access token for the proxy user
        Token.objects.create(user=proxy_user)

        return proxy_user

    def save(self, **kwargs):
        if not self.proxy_user:
            self.proxy_user = self._get_proxy_user()

        return super().save(**kwargs)

    def get_absolute_url(self):
        return reverse('applications:application.detail',
                       kwargs={'pk': self.pk})

