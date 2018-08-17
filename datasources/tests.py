from django.test import TestCase

from . import models


class DataSourceModelTest(TestCase):
    def test_string_representation(self):
        datasource = models.DataSource(name='Test Data Source')
        self.assertEqual(str(datasource), datasource.name)
