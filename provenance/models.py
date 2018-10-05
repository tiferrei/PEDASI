import json

from django import apps
from django.conf import settings
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone

import mongoengine
import prov.model

from applications.models import Application
from core.models import BaseAppDataModel
from datasources.models import DataSource

MAX_LENGTH_NAME_FIELD = 100


class ProvEntry(mongoengine.DynamicEmbeddedDocument):
    """
    Stored PROV record for a single action.

    e.g. Update a model's metadata, use a model.

    These will be embedded with a :class:`ProvCollection` record.
    """
    @classmethod
    def create_prov(cls,
                    instance: BaseAppDataModel,
                    user: settings.AUTH_USER_MODEL) -> 'ProvEntry':
        document = prov.model.ProvDocument(namespaces={
            'piot': 'http://www.pedasi-iot.org/',
            'foaf': 'http://xmlns.com/foaf/0.1/'
        })

        entity = document.entity(
            'piot:e2',
            {

                'piot:url': instance.get_absolute_url(),
            }
        )

        activity = document.activity(
            'piot:a1',
            timezone.now(),
            None,
            {
                prov.model.PROV_TYPE: 'edit',
            }
        )

        agent = document.agent(
            'piot:' + user.username,
            {
                # 'prov:type': prov.model.PROV['Person'],
                'prov:type': 'prov:Person',
                'foaf:givenName': user.first_name,
                'foaf:mbox': '<mailto:' + user.email + '>'
            }
        )

        # PROV library does not appear to be able to give a Python dictionary directly - have to go via string
        return cls.deserialize(content=document.serialize())

    def serialize(self):
        raise NotImplementedError

    @classmethod
    def deserialize(cls, source=None, content=None, format='json', **kwargs):
        if source is None and content is not None and format == 'json':
            json_string = content

        else:
            document = prov.model.ProvDocument.deserialize(source, content, format, **kwargs)
            json_string = document.serialize(format='json')

        # PROV library does not appear to be able to give a Python dictionary directly - have to go via string
        prov_json = json.loads(json_string)
        return cls(**prov_json)


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
    entries = mongoengine.fields.EmbeddedDocumentListField(
        document_type=ProvEntry,
        default=[]
    )

    @property
    def instance(self):
        model = apps.apps.get_model(self.app_label, self.model_name)
        return model.objects.get(pk=self.related_pk)

    @classmethod
    def for_model_instance(cls, instance: BaseAppDataModel) -> 'ProvCollection':
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
    record = ProvEntry.create_prov(
        instance,
        instance.owner
    )

    obj.entries.append(record)
    obj.save()
