from django.contrib.auth import get_user_model
from django.test import TestCase

from . import models


class ApplicationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.user = cls.user_model.objects.create_user('test')

    def test_string_representation(self):
        application = models.Application(name='Test Application',
                                         owner=self.user)
        self.assertEqual(str(application), application.name)

    def test_db_store(self):
        """
        Test that Applications are able to be stored in a database.

        Catches regression when making changes to database routers.
        """
        application = models.Application.objects.create(name='Test Application',
                                                        owner=self.user)

        application_read, created = models.Application.objects.get_or_create(pk=application.pk)

        self.assertFalse(created)
        self.assertEqual(application, application_read)
