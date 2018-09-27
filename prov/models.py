from django.db import models as django_models
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone

import mongoengine

from applications.models import Application
from datasources.models import DataSource

MAX_LENGTH_NAME_FIELD = 100


class ProvEntry(mongoengine.EmbeddedDocument):
    """
    Stored PROV record for a single action.

    e.g. Update a model's metadata, use a model.

    These will be embedded with a :class:`ProvCollection` record.
    """
    #: Time at which the action occurred
    time = mongoengine.fields.DateTimeField(default=timezone.now(),
                                            required=True, null=False)


class ProvCollection(mongoengine.Document):
    """
    The complete set of PROV records storing all actions performed on a single model instance.

    These are managed using MongoEngine rather than as a Django model
    """
    #: App from which the model comes
    app_label = mongoengine.fields.StringField(max_length=MAX_LENGTH_NAME_FIELD,
                                               required=True, null=False)

    #: Name of the model
    model_name = mongoengine.fields.StringField(max_length=MAX_LENGTH_NAME_FIELD,
                                                required=True, null=False)

    # TODO should this be editable=False?  Can a model PK change?
    # TODO can we make this behave like a primary key?
    #: Primary key of the model instance
    related_pk = mongoengine.fields.IntField(required=True, null=False)

    #: List of ProvEntry actions
    entries = mongoengine.fields.EmbeddedDocumentListField(document_type=ProvEntry,
                                                           default=[])

    @classmethod
    def for_model_instance(cls, instance: django_models.Model) -> 'ProvCollection':
        """
        Get the :class:`ProvCollection` instance related to a particular model instance.

        Create a :class:`ProvCollection` instance if there is not one already.

        :param instance: Model instance for which to get :class:`ProvCollection`
        :return: :class:`ProvCollection` instance
        """
        # mongoengine doesn't have an upsert operation like get_or_create
        try:
            record = cls.objects.get(
                app_label=instance._meta.app_label,
                model_name=instance._meta.model_name,
                related_pk=instance.pk
            )
        except mongoengine.errors.DoesNotExist:
            record = cls(
                app_label=instance._meta.app_label,
                model_name=instance._meta.model_name,
                related_pk=instance.pk
            )
            record.save()

        return record


@receiver(signals.post_save, sender=Application)
@receiver(signals.post_save, sender=DataSource)
def save_prov(sender, instance, **kwargs):
    """
    Signal receiver to update a ProvCollection when a PROV tracked model is saved.
    """
    obj = ProvCollection.for_model_instance(instance)

    # TODO create meaningful prov entry
    obj.entries.append(ProvEntry())
    obj.save()
