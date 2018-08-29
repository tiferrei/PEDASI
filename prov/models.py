from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone

from djongo import models

from applications.models import Application
from datasources.models import DataSource

MAX_LENGTH_NAME_FIELD = 100


class ProvEntry(models.Model):
    time = models.DateTimeField(default=timezone.now,
                                blank=False, null=False)

    class Meta:
        # Make this model abstract to avoid creating a table
        # since it will only be used inside a ProvCollection model
        abstract = True


class ProvCollection(models.Model):
    app_label = models.CharField(max_length=MAX_LENGTH_NAME_FIELD,
                                 blank=False, null=False)

    model_name = models.CharField(max_length=MAX_LENGTH_NAME_FIELD,
                                  blank=False, null=False)

    related_pk = models.PositiveIntegerField(blank=False, null=False)

    entries = models.ArrayModelField(
        model_container=ProvEntry,
        default=[],
        blank=True, null=False
    )

    @classmethod
    def for_model_instance(cls, model: models.Model):
        obj, created = cls.objects.get_or_create(
            app_label=model._meta.app_label,
            model_name=model._meta.model_name,
            related_pk=model.pk
        )

        return obj

    @staticmethod
    @receiver(signals.post_save, sender=Application)
    @receiver(signals.post_save, sender=DataSource)
    def save_prov(sender, instance, **kwargs):
        obj = ProvCollection.for_model_instance(instance)

        obj.entries.append(ProvEntry())
        obj.save()
