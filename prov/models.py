from django.db.models import signals
from django.dispatch import receiver

from djongo import models

from applications.models import Application
from datasources.models import DataSource

MAX_LENGTH_NAME_FIELD = 100


class ProvEntry(models.Model):
    """
    Stored PROV record for a single action.

    e.g. Update a model's metadata, use a model.
    """
    #: Time at which the action occurred
    time = models.DateTimeField(auto_now_add=True,
                                editable=False,
                                blank=False, null=False)

    class Meta:
        # Make this model abstract to avoid creating a table
        # since it will only be used inside a ProvCollection model
        abstract = True


class ProvCollection(models.Model):
    """
    The complete set of PROV records storing all actions performed on a single model instance.
    """
    #: App from which the model comes
    app_label = models.CharField(max_length=MAX_LENGTH_NAME_FIELD,
                                 editable=False,
                                 blank=False, null=False)

    #: Name of the model
    model_name = models.CharField(max_length=MAX_LENGTH_NAME_FIELD,
                                  editable=False,
                                  blank=False, null=False)

    # TODO should this be editable=False?  Can a model PK change?
    #: Primary key of the model instance
    related_pk = models.PositiveIntegerField(blank=False, null=False)

    #: List of ProvEntry actions
    entries = models.ArrayModelField(
        model_container=ProvEntry,
        default=[],
        blank=True, null=False
    )

    @classmethod
    def for_model_instance(cls, instance: models.Model) -> 'ProvCollection':
        """
        Get the :class:`ProvCollection` instance related to a particular model instance.

        Create a :class:`ProvCollection` instance if there is not one already.

        :param instance: Model instance for which to get :class:`ProvCollection`
        :return: :class:`ProvCollection` instance
        """
        obj, created = cls.objects.get_or_create(
            app_label=instance._meta.app_label,
            model_name=instance._meta.model_name,
            related_pk=instance.pk
        )

        return obj


@receiver(signals.post_save, sender=Application)
@receiver(signals.post_save, sender=DataSource)
def save_prov(sender, instance, **kwargs):
    """
    Signal receiver to update a ProvCollection when a PROV tracked model is saved.
    """
    obj = ProvCollection.for_model_instance(instance)

    obj.entries.append(ProvEntry())
    obj.save()
