"""
This module contains models related to the quality assessment of data sources.
"""

from django.db import models

from core.models import MAX_LENGTH_NAME
from .datasource import DataSource
from .metadata import MetadataField


class QualityRuleset(models.Model):
    """
    A ruleset for assessing the quality of a data source.
    """
    class Meta:
        unique_together = (('name', 'version',),)

    #: Name of the ruleset
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    #: Short text identifier
    short_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                  unique=True, blank=True, null=False)

    #: Ruleset version - distinguishes successive versions of the same set
    version = models.CharField(max_length=MAX_LENGTH_NAME,
                               blank=False, null=False)

    def __call__(self, datasource: DataSource) -> int:
        raise NotImplementedError


class QualityLevel(models.Model):
    """
    A set of criteria that is required to grant a particular quality level.
    """
    class Meta:
        unique_together = (('ruleset', 'level'),)

    #: Which ruleset does this level belong to?
    ruleset = models.ForeignKey(QualityRuleset, related_name='levels',
                                on_delete=models.CASCADE,
                                blank=False, null=False)

    #: What level is this?
    level = models.PositiveSmallIntegerField(blank=False, null=False)

    #: Threshold level that must be exceeded by criteria weights to pass this level
    threshold = models.FloatField(blank=True, null=True)

    def __call__(self, datasource: DataSource) -> bool:
        """
        Does a data source pass the criteria for this quality level?

        :param datasource: Data source to assess
        :return: Passes this quality level?
        """
        raise NotImplementedError


class QualityCriterion(models.Model):
    """
    A weighted criterion to determine whether a data source meets a certain quality level.
    """
    class Meta:
        unique_together = (('quality_level', 'metadata_field'),)

    #: Which quality level does this criterion belong to?
    quality_level = models.ForeignKey(QualityLevel, related_name='criteria',
                                      on_delete=models.CASCADE,
                                      blank=False, null=False)

    #: Which metadata field represents this criterion?
    metadata_field = models.ForeignKey(MetadataField, related_name='+',
                                       on_delete=models.PROTECT,
                                       blank=False, null=False)

    #: What proportion of the quality level does this criterion provide?
    weight = models.FloatField(default=1,
                               blank=False, null=False)

    def __call__(self, datasource: DataSource) -> float:
        """
        Weight provided to the quality level based on passing or failing this criterion.

        :param datasource: Data source to assess
        :return: Weight provided to the quality level from passing or failing this criterion
        """
        raise NotImplementedError




