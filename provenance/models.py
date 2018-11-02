import enum
import json
import typing
import uuid

from django import apps
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

import mongoengine
from mongoengine.queryset.visitor import Q
import prov.model

from applications.models import Application
from core.models import BaseAppDataModel
from datasources.models import DataSource

MAX_LENGTH_NAME_FIELD = 100


class PedasiDummyApplication:
    name = 'PEDASI'
    pk = 'pedasi'  # We convert pk to string anyway - so this is fine

    @staticmethod
    def get_absolute_url():
        # TODO don't hardcode URL
        return 'http://www.pedasi-iot.org/'


@enum.unique
class ProvActivity(enum.Enum):
    UPDATE = 'piot:update'
    ACCESS = 'piot:access'


class ProvEntry(mongoengine.DynamicDocument):
    """
    Stored PROV record for a single action.

    e.g. Update a model's metadata, use a model.

    These will be referred to by a :class:`ProvWrapper` document.
    """
    @classmethod
    def create_prov(cls,
                    instance: BaseAppDataModel,
                    user_uri: str,
                    application: typing.Optional[Application] = None,
                    activity_type: typing.Optional[ProvActivity] = ProvActivity.UPDATE) -> 'ProvEntry':
        document = prov.model.ProvDocument(namespaces={
            'piot': 'http://www.pedasi-iot.org/',
            'foaf': 'http://xmlns.com/foaf/0.1/',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
        })

        entity = document.entity(
            # TODO unique identifier for instance
            'piot:e-' + slugify(instance._meta.model_name[0]) + str(instance.pk),
            other_attributes={
                prov.model.PROV_TYPE: 'piot:' + slugify(instance._meta.model_name),
                'xsd:anyURI': instance.get_absolute_url(),
            }
        )

        activity = document.activity(
            'piot:a-' + str(uuid.uuid4()),
            timezone.now(),
            None,
            other_attributes={
                prov.model.PROV_TYPE: activity_type.value
            }
        )

        agent_user = document.agent(
            # Generate a UUID so we can lookup records belonging to a user
            # But not identify the user from a given record
            # TODO how strongly do we want to prevent user identification?
            # See https://github.com/Southampton-RSG/PEDASI-IoT/issues/10
            'piot:u-' + str(uuid.uuid5(uuid.NAMESPACE_URL, user_uri)),
            other_attributes={
                prov.model.PROV_TYPE: 'prov:Person',
            }
        )

        if application is None:
            application = PedasiDummyApplication

        agent_application = document.agent(
            'piot:app-' + str(application.pk),
            other_attributes={
                prov.model.PROV_TYPE: 'prov:SoftwareAgent',
                'xsd:anyURI': application.get_absolute_url(),
            }
        )

        document.actedOnBehalfOf(
            agent_application,      # User who performs the action, on behalf of...
            agent_user,             # User who is responsible
            activity,               # NB: The prov library documentation suggests these are the other way round
            other_attributes={
                prov.model.PROV_TYPE: 'piot:ApplicationAction',
            }
        )

        # PROV library does not appear to be able to give a Python dictionary directly - have to go via string
        return cls.deserialize(content=document.serialize())

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


class ProvWrapper(mongoengine.Document):
    """
    Wrapper around a single PROV record (:class:`ProvEntry`) which allows it to be easily linked to an instance
    of a Django model.

    This is managed using MongoEngine rather than as a Django model.
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

    #: The actual PROV entry
    entry = mongoengine.fields.ReferenceField(
        document_type=ProvEntry
    )

    @property
    def instance(self):
        """
        Return the Django model instance to which this :class:`ProvWrapper` refers.
        """
        model = apps.apps.get_model(self.app_label, self.model_name)
        return model.objects.get(pk=self.related_pk)

    @classmethod
    def filter_model_instance(cls, instance: BaseAppDataModel) -> typing.Generator[ProvEntry, None, None]:
        """
        Get all :class:`ProvEntry` documents related to a particular Django model instance.

        :param instance: Model instance for which to get all :class:`ProvEntry`s
        :return: List of :class:`ProvEntry`s
        """
        # TODO return a queryset rather than a generator
        for wrapper in ProvWrapper.objects(
            Q(app_label=instance._meta.app_label) &
            Q(model_name=instance._meta.model_name) &
            Q(related_pk=instance.pk)
        ):
            yield wrapper.entry

    @classmethod
    def create_prov(cls,
                    instance: BaseAppDataModel,
                    user_uri: str,
                    application: typing.Optional[Application] = None,
                    activity_type: typing.Optional[ProvActivity] = ProvActivity.UPDATE) -> ProvEntry:
        """
        Create a PROV record for a single action.

        e.g. Update a model's metadata, use a model.

        These will create and return a :class:`ProvEntry` document.
        """
        prov_entry = ProvEntry.create_prov(instance, user_uri,
                                           application=application,
                                           activity_type=activity_type)
        prov_entry.save()

        wrapper = cls(
            app_label=instance._meta.app_label,
            model_name=instance._meta.model_name,
            related_pk=instance.pk,
            entry=prov_entry
        )
        wrapper.save()

        return prov_entry

    def delete(self, signal_kwargs=None, **write_concern):
        """
        Delete this document and the :class:`ProvEntry` to which it refers.
        """
        self.entry.delete(signal_kwargs, **write_concern)
        super().delete(signal_kwargs, **write_concern)


@receiver(signals.post_save, sender=Application)
@receiver(signals.post_save, sender=DataSource)
def save_prov(sender, instance, **kwargs):
    """
    Signal receiver to create a :class:`ProvEntry` when a PROV tracked model is saved.
    """
    ProvWrapper.create_prov(
        instance,
        # TODO what if an admin edits a model?
        instance.owner.get_uri(),
        activity_type=ProvActivity.UPDATE
    )
