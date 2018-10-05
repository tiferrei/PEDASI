import json
import pathlib
import unittest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

import jsonschema
import mongoengine

from datasources.models import DataSource
from provenance import models


# Create connection to test DB
mongoengine.connect('test_prov')


class ProvEntryTest(TestCase):
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

    def test_prov_created(self):
        entry = models.ProvEntry.create_prov(self.datasource, self.user)

        self.assertIsNotNone(entry)

    def test_prov_schema(self):
        """
        Validate :class:`ProvEntry` against PROV-JSON schema.
        """
        entry = models.ProvEntry.create_prov(self.datasource, self.user)
        entry_json = json.loads(entry.to_json())

        with open(pathlib.Path(settings.BASE_DIR).joinpath('provenance', 'data', 'prov-json.schema.json')) as fp:
            schema = json.loads(fp.read())

        validator = jsonschema.Draft4Validator(schema)

        try:
            validator.validate(entry_json)
        except jsonschema.exceptions.ValidationError:
            for error in validator.iter_errors(entry_json):
                print(error.message)
            raise


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

    def tearDown(self):
        # Have to delete instance manually since we're not using Django's database manager
        models.ProvCollection.for_model_instance(self.datasource).delete()

    def test_prov_datasource_create(self):
        """
        Test that a PROV collection / entry is created when a model is created.
        """
        # PROV record should be created when model is created
        prov_collection = models.ProvCollection.for_model_instance(self.datasource)
        self.assertEqual(len(prov_collection.entries), 1)

    def test_prov_datasource_update(self):
        """
        Test that a new PROV entry is created when a model is updated.
        """
        prov_collection = models.ProvCollection.for_model_instance(self.datasource)
        n_provs = len(prov_collection.entries)

        self.datasource.plugin_name = 'CHANGED'
        self.datasource.save()

        # Another PROV record should be created when model is changed and saved
        prov_collection = models.ProvCollection.for_model_instance(self.datasource)
        self.assertEqual(len(prov_collection.entries), n_provs + 1)

    @unittest.expectedFailure
    def test_prov_datasource_null_update(self):
        """
        Test that no new PROV entry is created when a model is saved without changes.
        """
        prov_collection = models.ProvCollection.for_model_instance(self.datasource)
        n_provs = len(prov_collection.entries)

        self.datasource.save()

        # No PROV record should be created when saving a model that has not changed
        prov_collection = models.ProvCollection.for_model_instance(self.datasource)
        self.assertEqual(len(prov_collection.entries), n_provs)

    def test_prov_records_distinct(self):
        """
        Test that a distinct PROV collection is created for each model instance.
        """
        prov_collection = models.ProvCollection.for_model_instance(self.datasource)

        new_datasource = DataSource.objects.create(
            name='Another Test Data Source',
            url='http://www.example.com',
            owner=self.user,
            plugin_name='TEST'
        )
        new_prov_collection = models.ProvCollection.for_model_instance(new_datasource)

        self.assertIsNot(prov_collection, new_prov_collection)

        self.assertEqual(prov_collection.related_pk, self.datasource.pk)
        self.assertEqual(new_prov_collection.related_pk, new_datasource.pk)
