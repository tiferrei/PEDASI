from django.contrib.auth import get_user_model
from django.test import TestCase

from datasources.models import DataSource
from prov.models import ProvCollection


class ProvCollectionTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user('test')

        self.datasource = DataSource.objects.create(
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

