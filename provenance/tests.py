"""
Tests for PROV tracking functionality and the models required to support it.
"""

import json
import pathlib
import unittest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

import jsonschema
import mongoengine
from mongoengine.queryset.visitor import Q

from datasources.models import DataSource
from provenance import models


# Create connection to test DB
TEST_DB = mongoengine.connect('test_prov')
TEST_DB.drop_database('test_prov')


class ProvEntryTest(TestCase):
    """
    Test the :class:`ProvEntry` model in isolation.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.user = cls.user_model.objects.create_user('Test Prov User')

    def setUp(self):
        self.datasource = DataSource.objects.create(
            name='Test Data Source',
            url='http://www.example.com',
            owner=self.user,
            plugin_name='TEST'
        )

    def tearDown(self):
        # Have to delete instance manually since we're not using Django's database manager
        datasource_type = ContentType.objects.get_for_model(DataSource)

        models.ProvWrapper.objects(
            Q(app_label=datasource_type.app_label) &
            Q(model_name=datasource_type.model) &
            Q(related_pk=self.datasource.pk)
        ).delete()

    def test_prov_created(self):
        """
        Test the creation of a :class:`ProvEntry` in isolation.
        """
        entry = models.ProvEntry.create_prov(self.datasource,
                                             self.user.get_uri())

        self.assertIsNotNone(entry)

    # TODO test content of PROV document - not just compliance to spec
    def test_prov_schema(self):
        """
        Validate :class:`ProvEntry` against PROV-JSON schema.
        """
        entry = models.ProvEntry.create_prov(self.datasource,
                                             self.user.get_uri())
        entry_json = json.loads(entry.to_json())

        schema_path = pathlib.Path(settings.BASE_DIR).joinpath('provenance', 'data', 'prov-json.schema.json')
        with open(schema_path) as schema_file:
            schema = json.load(schema_file)

        validator = jsonschema.Draft4Validator(schema)

        try:
            validator.validate(entry_json)
        except jsonschema.exceptions.ValidationError:
            for error in validator.iter_errors(entry_json):
                print(error.message)
            raise


class ProvWrapperTest(TestCase):
    """
    Test the wrapper that allows us to look up :class:`ProvEntry`s for a given object.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.user = cls.user_model.objects.create_user('Test Prov User')

    def setUp(self):
        self.datasource = DataSource.objects.create(
            name='Test Data Source',
            url='http://www.example.com',
            owner=self.user,
            plugin_name='TEST'
        )

    def tearDown(self):
        # Have to delete instance manually since we're not using Django's database manager
        datasource_type = ContentType.objects.get_for_model(DataSource)

        models.ProvWrapper.objects(
            Q(app_label=datasource_type.app_label) &
            Q(model_name=datasource_type.model) &
            Q(related_pk=self.datasource.pk)
        ).delete()

    @staticmethod
    def _count_prov(datasource: DataSource) -> int:
        prov_entries = models.ProvWrapper.filter_model_instance(datasource)
        return prov_entries.count()

    def test_prov_datasource_create(self):
        """
        Test that a :class:`ProvEntry` is created when a model is created.
        """
        # PROV record should be created when model is created
        self.assertEqual(self._count_prov(self.datasource), 1)

    def test_prov_datasource_update(self):
        """
        Test that a new :class:`ProvEntry` is created when a model is updated.
        """
        n_provs = self._count_prov(self.datasource)

        self.datasource.plugin_name = 'CHANGED'
        self.datasource.save()

        # Another PROV record should be created when model is changed and saved
        self.assertEqual(self._count_prov(self.datasource), n_provs + 1)

    @unittest.expectedFailure
    def test_prov_datasource_null_update(self):
        """
        Test that no new :class:`ProvEntry` is created when a model is saved without changes.
        """
        n_provs = self._count_prov(self.datasource)

        self.datasource.save()

        # No PROV record should be created when saving a model that has not changed
        self.assertEqual(self._count_prov(self.datasource), n_provs)

    def test_prov_records_distinct(self):
        """
        Test that :class:`ProvEntry`s are not reused.
        """
        prov_entries = models.ProvWrapper.filter_model_instance(self.datasource)

        new_datasource = DataSource.objects.create(
            name='Another Test Data Source',
            url='http://www.example.com',
            owner=self.user,
            plugin_name='TEST'
        )
        new_prov_entries = models.ProvWrapper.filter_model_instance(new_datasource)

        intersection = set(prov_entries).intersection(new_prov_entries)
        self.assertFalse(intersection)
