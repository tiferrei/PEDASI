"""
This module contains classes required to build a data pipeline from a series of data connectors.
"""

import abc
import json
import typing

import jsonschema

from core import plugin
from .. import models


class BasePipelineStage(metaclass=plugin.Plugin):
    """
    Base class for pipeline stages.  Allows the defined classes to be used as plugins.
    """
    #: Help string to be shown when a user is building a pipeline
    description = None

    def __init__(self, options: typing.Optional[typing.Mapping] = None):
        pass

    @abc.abstractmethod
    def __call__(self, data: typing.Mapping) -> typing.Mapping:
        """
        Pass data through the pipeline stage.

        :param data: Data to process
        :return: Processed data
        """
        raise NotImplementedError


class NullPipelineStage(BasePipelineStage):
    """
    Pipeline stage which does nothing.  For testing purposes.
    """
    #: Help string to be shown when a user is building a pipeline
    description = 'Does nothing'

    def __call__(self, data: typing.Mapping) -> typing.Mapping:
        return data


class JsonValidationPipelineStage(BasePipelineStage):
    """
    Validate returned data against a JSON schema.
    """
    #: Help string to be shown when a user is building a pipeline
    description = 'Validates data against a JSON schema'

    def __init__(self, options: typing.Optional[typing.Mapping] = None):
        super().__init__(options)

        try:
            self.schema = options['schema']

        except KeyError as e:
            raise models.pipeline.PipelineSetupError('Schema has not been defined') from e

    def __call__(self, data: typing.Mapping) -> typing.Mapping:
        try:
            jsonschema.validate(data, json.loads(self.schema))

        except jsonschema.ValidationError as e:
            raise models.pipeline.PipelineValidationError('Failed validation stage: ' + str(e))

        return data
