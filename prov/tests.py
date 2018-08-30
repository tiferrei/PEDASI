import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase

from datasources.models import DataSource
from prov.models import ProvCollection


class ProvCollectionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.user = cls.user_model.objects.create_user('test')

    def setUp(self):
        self.datasource = DataSource.objects.create(
            name='Test Data Source',
            url='http://www.example.com',
            owner=self.user,
            plugin_name='TEST'
        )

    def test_prov_datasource_create(self):
        """
        Test that a PROV collection / entry is created when a model is created.
        """
        # PROV record should be created when model is created
        prov_collection = ProvCollection.for_model_instance(self.datasource)
        self.assertEqual(len(prov_collection.entries), 1)

    def test_prov_datasource_update(self):
        """
        Test that a new PROV entry is created when a model is updated.
        """
        prov_collection = ProvCollection.for_model_instance(self.datasource)
        n_provs = len(prov_collection.entries)

        self.datasource.plugin_name = 'CHANGED'
        self.datasource.save()

        # Another PROV record should be created when model is changed and saved
        prov_collection = ProvCollection.for_model_instance(self.datasource)
        self.assertEqual(len(prov_collection.entries), n_provs + 1)

    @unittest.expectedFailure
    def test_prov_datasource_null_update(self):
        """
        Test that no new PROV entry is created when a model is saved without changes.
        """
        prov_collection = ProvCollection.for_model_instance(self.datasource)
        n_provs = len(prov_collection.entries)

        self.datasource.save()

        # No PROV record should be created when saving a model that has not changed
        prov_collection = ProvCollection.for_model_instance(self.datasource)
        self.assertEqual(len(prov_collection.entries), n_provs)

    def test_prov_records_distinct(self):
        """
        Test that a distinct PROV collection is created for each model instance.
        """
        prov_collection = ProvCollection.for_model_instance(self.datasource)

        new_datasource = DataSource.objects.create(
            name='Another Test Data Source',
            url='http://www.example.com',
            owner=self.user,
            plugin_name='TEST'
        )
        new_prov_collection = ProvCollection.for_model_instance(new_datasource)

        self.assertIsNot(prov_collection, new_prov_collection)

        self.assertEqual(prov_collection.related_pk, self.datasource.pk)
        self.assertEqual(new_prov_collection.related_pk, new_datasource.pk)
