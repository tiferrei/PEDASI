from django.utils import timezone

from djongo import models

from datasources.models import DataSource

MAX_LENGTH_NAME_FIELD = 100


class ProvEntry(models.Model):
    time = models.DateTimeField(default=timezone.now,
                                blank=False, null=False)

    class Meta:
        abstract = True


class ProvCollection(models.Model):
    app_name = models.CharField(max_length=MAX_LENGTH_NAME_FIELD,
                                blank=False, null=False)

    model_name = models.CharField(max_length=MAX_LENGTH_NAME_FIELD,
                                  blank=False, null=False)

    related_pk = models.PositiveIntegerField(blank=False, null=False)

    entries = models.ArrayModelField(
        model_container=ProvEntry
    )
