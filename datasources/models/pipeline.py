import typing

from django.conf import settings
from django.db import models

from core.models import MAX_LENGTH_NAME
from ..pipeline.base import BasePipelineStage


class PipelineRuntimeError(BaseException):
    pass


class PipelineValidationError(PipelineRuntimeError):
    pass


class PipelineSetupError(BaseException):
    pass


class Pipeline(models.Model):
    """
    Model representing a data pipeline.

    A pipeline may contain multiple stages.
    """
    # Prevent template engine from trying to call the model
    do_not_call_in_templates = True

    #: User who has responsibility for this licence
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              limit_choices_to={
                                  'groups__name': 'Data providers'
                              },
                              on_delete=models.PROTECT,
                              related_name='pipelines',
                              blank=False, null=False)

    #: Name of this pipeline
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    def __call__(self, data: typing.Mapping,
                 options: typing.Optional[typing.Mapping] = None) -> typing.Mapping:
        """
        Run data through this pipeline.

        :param data: Data to be passed through the pipeline
        :return: Processed data
        """
        for stage in self.stages.all():
            data = stage(data, options=options)

        return data

    def __str__(self):
        return self.name


class PipelineStage(models.Model):
    """
    Model representing a stage of a data pipeline.
    """
    class Meta:
        order_with_respect_to = 'pipeline'

    # Prevent template engine from trying to call the model
    do_not_call_in_templates = True

    #: Which pipeline plugin is being used?
    plugin_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                   default='NullPipelineStage',
                                   blank=False, null=False)

    #: Which pipeline does this belong to?
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE,
                                 related_name='stages',
                                 blank=False, null=False)

    def __call__(self, data: typing.Mapping,
                 options: typing.Optional[typing.Mapping] = None) -> typing.Mapping:
        """
        Run data through this pipeline stage.

        :param data: Data to be passed through the pipeline stage
        :return: Processed data
        """
        BasePipelineStage.load_plugins('datasources/pipeline')

        plugin = BasePipelineStage.get_plugin(self.plugin_name)

        return plugin(options=options)(data)

    def __str__(self):
        return self.plugin_name
