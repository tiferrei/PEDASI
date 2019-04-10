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

        cls.metadata_field = models.MetadataField.objects.create(
            name='Test Metadata Field 1',
            short_name='TMF1'
        )

    def setUp(self):
        super().setUp()

        self.ruleset = models.QualityRuleset.objects.create(
            name='Test Ruleset 1',
            short_name='TR1v1',
            version='1'
        )

        self.datasource = models.DataSource.objects.create(
            name='Test Data Source 1',
            owner=self.user
        )

    def test_create_ruleset(self):
        ruleset = models.QualityRuleset.objects.get(
            short_name='TR1v1'
        )

        self.assertEqual('Test Ruleset 1', ruleset.name)
        self.assertEqual('TR1v1', ruleset.short_name)
        self.assertEqual('1', ruleset.version)

        return ruleset

    def test_ruleset_eval_null(self):
        """
        Test that an empty ruleset identifies any datasource as level 0.
        """
        level = self.ruleset(self.datasource)

        self.assertEqual(0, level)

    def test_ruleset_create_level(self):
        """
        Test that levels can be added to rulesets.
        """
        self.ruleset.levels.create(
            level=1
        )

        self.assertEqual(1, self.ruleset.levels.count())

    def test_ruleset_create_criterion(self):
        """
        Test that criteria can be added to quality levels.
        """
        level_1 = self.ruleset.levels.create(
            level=1
        )

        level_1.criteria.create(
            metadata_field=self.metadata_field
        )

        self.assertEqual(1, level_1.criteria.count())

    def test_ruleset_eval_criterion(self):
        """
        Test that criteria are evaluated correctly.

        Should return weight contributed to level threshold.
        """
        level_1 = self.ruleset.levels.create(
            level=1,
            threshold=1
        )

        criterion = level_1.criteria.create(
            metadata_field=self.metadata_field,
            weight=1
        )

        self.assertEqual(1, level_1.criteria.count())

        self.assertAlmostEqual(0, criterion(self.datasource))

        self.datasource.metadata_items.create(
            field=self.metadata_field,
            value=''
        )

        self.assertAlmostEqual(1, criterion(self.datasource))

    def test_ruleset_eval_level(self):
        """
        Test that quality levels are evaluated correctly.

        Should return whether data source passes level threshold.
        """
        level_1 = self.ruleset.levels.create(
            level=1,
            threshold=1
        )

        level_1.criteria.create(
            metadata_field=self.metadata_field,
            weight=1
        )

        self.assertFalse(level_1(self.datasource))

        self.datasource.metadata_items.create(
            field=self.metadata_field,
            value=''
        )

        self.assertTrue(level_1(self.datasource))

    def test_ruleset_eval(self):
        """
        Test that rulesets are evaluated correctly.

        Should return quality level of data source.
        """
        level_1 = self.ruleset.levels.create(
            level=1,
            threshold=1
        )

        level_1.criteria.create(
            metadata_field=self.metadata_field,
            weight=1
        )

        self.assertEqual(0, self.ruleset(self.datasource))

        self.datasource.metadata_items.create(
            field=self.metadata_field,
            value=''
        )

        self.assertEqual(1, self.ruleset(self.datasource))

