from django.contrib.auth import get_user_model
from django.test import TestCase

from datasources import models


class QualityRulesetTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create_user(
            username='Test User 1'
        )

    def test_create_ruleset(self):
        ruleset = models.QualityRuleset.objects.create(
            name='Test Ruleset 1',
            short_name='TR1v1',
            version='1'
        )

        ruleset = models.QualityRuleset.objects.get(
            short_name='TR1v1'
        )

        self.assertEqual('Test Ruleset 1', ruleset.name)
        self.assertEqual('TR1v1', ruleset.short_name)
        self.assertEqual('1', ruleset.version)

        return ruleset

    def test_ruleset_eval_null(self):
        ruleset = models.QualityRuleset.objects.create(
            name='Test Ruleset 1',
            short_name='TR1v1',
            version='1'
        )

        datasource = models.DataSource.objects.create(
            name='Test Data Source 1',
            owner=self.user
        )

        level = ruleset(datasource)

        self.assertEqual(0, level)

    def test_ruleset_create_level(self):
        ruleset = models.QualityRuleset.objects.create(
            name='Test Ruleset 1',
            short_name='TR1v1',
            version='1'
        )

        ruleset.levels.create(
            level=1
        )

        self.assertEqual(1, ruleset.levels.count())

    def test_ruleset_create_criterion(self):
        metadata_field = models.MetadataField.objects.create(
            name='Test Metadata Field 1',
            short_name='TMF1'
        )

        ruleset = models.QualityRuleset.objects.create(
            name='Test Ruleset 1',
            short_name='TR1v1',
            version='1'
        )

        level_1 = ruleset.levels.create(
            level=1
        )

        level_1.criteria.create(
            metadata_field=metadata_field
        )

        self.assertEqual(1, level_1.criteria.count())

    def test_ruleset_eval_criterion(self):
        metadata_field = models.MetadataField.objects.create(
            name='Test Metadata Field 1',
            short_name='TMF1'
        )

        datasource = models.DataSource.objects.create(
            name='Test Data Source 1',
            owner=self.user
        )

        ruleset = models.QualityRuleset.objects.create(
            name='Test Ruleset 1',
            short_name='TR1v1',
            version='1'
        )

        level_1 = ruleset.levels.create(
            level=1,
            threshold=1
        )

        criterion = level_1.criteria.create(
            metadata_field=metadata_field,
            weight=1
        )

        self.assertEqual(1, level_1.criteria.count())

        self.assertAlmostEqual(0, criterion(datasource))

        datasource.metadata_items.create(
            field=metadata_field,
            value=''
        )

        self.assertAlmostEqual(1, criterion(datasource))

    def test_ruleset_eval_level(self):
        metadata_field = models.MetadataField.objects.create(
            name='Test Metadata Field 1',
            short_name='TMF1'
        )

        datasource = models.DataSource.objects.create(
            name='Test Data Source 1',
            owner=self.user
        )

        ruleset = models.QualityRuleset.objects.create(
            name='Test Ruleset 1',
            short_name='TR1v1',
            version='1'
        )

        level_1 = ruleset.levels.create(
            level=1
            # threshold=1
        )

        level_1.criteria.create(
            metadata_field=metadata_field,
            weight=1
        )

        self.assertFalse(level_1(datasource))

        datasource.metadata_items.create(
            field=metadata_field,
            value=''
        )

        self.assertTrue(level_1(datasource))

    def test_ruleset_eval(self):
        metadata_field = models.MetadataField.objects.create(
            name='Test Metadata Field 1',
            short_name='TMF1'
        )

        datasource = models.DataSource.objects.create(
            name='Test Data Source 1',
            owner=self.user
        )

        ruleset = models.QualityRuleset.objects.create(
            name='Test Ruleset 1',
            short_name='TR1v1',
            version='1'
        )

        level_1 = ruleset.levels.create(
            level=1
            # threshold=1
        )

        level_1.criteria.create(
            metadata_field=metadata_field,
            weight=1
        )

        self.assertEqual(0, ruleset(datasource))

        datasource.metadata_items.create(
            field=metadata_field,
            value=''
        )

        self.assertEqual(1, ruleset(datasource))

