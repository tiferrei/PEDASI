"""
This module contains models for dynamic assignment of metadata to data sources.
"""

from django.core import validators
from django.db import models

from core.models import MAX_LENGTH_NAME
from .datasource import DataSource, MAX_LENGTH_REASON


class MetadataField(models.Model):
    """
    A metadata field that can be dynamically added to a data source.

    Operational MetadataFields are those which have some associated code within PEDASI.
    They should be present within any deployment of PEDASI.

    Current operational metadata fields are (by short_name):
    - data_query_param
    - indexed_field
    """
    #: Name of the field
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            unique=True,
                            blank=False, null=False)

    #: Short text identifier for the field
    short_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        validators=[
            validators.RegexValidator(
                r'^[a-zA-Z][a-zA-Z0-9_]*\Z',
                'Short name must begin with a letter and consist only of letters, numbers and underscores.',
                'invalid'
            )
        ],
        unique=True,
        blank=False, null=False
    )

    #: Does the field have an operational effect within PEDASI?
    operational = models.BooleanField(default=False,
                                      blank=False, null=False)

    def __str__(self):
        return self.name

    @classmethod
    def load_inline_fixtures(cls):
        """
        Create any instances required for the functioning of PEDASI.

        This is called from within the AppConfig.
        """
        fixtures = (
            ('data_query_param', 'data_query_param', True),
            ('indexed_field', 'indexed_field', True),
        )

        for name, short_name, operational in fixtures:
            obj, created = cls.objects.get_or_create(
                short_name=short_name
            )
            obj.name = name
            obj.operational = operational
            obj.save()


class MetadataItem(models.Model):
    """
    The value of the metadata field on a given data source.
    """
    #: The value of this metadata field
    value = models.CharField(max_length=MAX_LENGTH_REASON,
                             blank=True, null=False)

    #: To which field does this relate?
    field = models.ForeignKey(MetadataField,
                              related_name='values',
                              on_delete=models.PROTECT,
                              blank=False, null=False)

    #: To which data source does this relate?
    datasource = models.ForeignKey(DataSource,
                                   related_name='metadata_items',
                                   on_delete=models.CASCADE,
                                   blank=False, null=False)

    class Meta:
        unique_together = (('field', 'datasource', 'value'),)

    def __str__(self):
        return self.value
