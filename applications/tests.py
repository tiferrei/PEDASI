from django.test import TestCase

from . import models


class ApplicationModelTest(TestCase):
    def test_string_representation(self):
        application = models.Application(name='Test Application')
        self.assertEqual(str(application), application.name)
