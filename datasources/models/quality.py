"""
This module contains models related to the quality assessment of data sources.
"""
import itertools

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

    # Prevent template engine from trying to call the model
    do_not_call_in_templates = True

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
        """
        Evaluate a data source to get its quality level under this ruleset.

        :param datasource: Data source to assess
        :return: Quality level of data source
        """
        # Get list of all levels that the data source passes - stop when a fail is encountered
        passes = list(
            itertools.takewhile(
                lambda x: x(datasource),
                self.levels.all()
            )
        )

        try:
            # Highest passed level will be the last in the list
            return passes[-1].level

        except IndexError:
            return 0

    def __str__(self):
        return '{0} - {1}'.format(self.name, self.version)


class QualityLevel(models.Model):
    """
    A set of criteria that is required to grant a particular quality level.
    """
    class Meta:
        unique_together = (('ruleset', 'level'),)
        ordering = ['level']

    # Prevent template engine from trying to call the model
    do_not_call_in_templates = True

    #: Which ruleset does this level belong to?
    ruleset = models.ForeignKey(QualityRuleset, related_name='levels',
                                on_delete=models.CASCADE,
                                blank=False, null=False)

    #: What level is this?
    level = models.PositiveSmallIntegerField(blank=False, null=False)

    #: Threshold level that must be exceeded by criteria weights to pass this level
    threshold = models.FloatField(blank=True, null=True)

    def __call__(self, datasource: DataSource, rtol: float = 1e-3) -> bool:
        """
        Does a data source pass the criteria for this quality level?

        :param datasource: Data source to assess
        :param rtol: Relative tolerance to compare floating point threshold
        :return: Passes this quality level?
        """
        threshold = self.threshold
        if threshold is None:
            threshold = self.criteria.aggregate(models.Sum('weight'))['weight__sum']

        total = sum(criterion(datasource) for criterion in self.criteria.all())

        # Compare using relative tolerance to account for floating point error
        return total >= (threshold * (1 - rtol))

    def __str__(self):
        return '{0} - level {1}'.format(self.ruleset, self.level)


class QualityCriterion(models.Model):
    """
    A weighted criterion to determine whether a data source meets a certain quality level.
    """
    class Meta:
        unique_together = (('quality_level', 'metadata_field'),)
        verbose_name_plural = 'quality criteria'

    # Prevent template engine from trying to call the model
    do_not_call_in_templates = True

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
        return self.weight if datasource.metadata_items.filter(field=self.metadata_field).exists() else 0

    def __str__(self):
        return '{0} - weight {1}'.format(self.metadata_field, self.weight)




