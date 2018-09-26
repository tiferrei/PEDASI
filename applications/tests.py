from django.test import TestCase

from . import models


class ApplicationModelTest(TestCase):
    def test_string_representation(self):
        application = models.Application(name='Test Application')
        self.assertEqual(str(application), application.name)

    def test_db_store(self):
        """
        Test that Applications are able to be stored in a database.

        Catches regression when making changes to database routers.
        """
        application = models.Application.objects.create(name='Test Application')

        application_read, created = models.Application.objects.get_or_create(name='Test Application')

        self.assertFalse(created)
        self.assertEqual(application, application_read)
