"""
This module contains classes required to build a data pipeline from a series of data connectors.
"""

import abc
import typing

from core import plugin


class BasePipelineStage(metaclass=plugin.Plugin):
    #: Help string to be shown when a user is building a pipeline
    description = None

    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def transform(self, data: typing.Mapping) -> typing.Mapping:
        raise NotImplementedError


class NullPipelineStage(BasePipelineStage):
    """
    Base class for pipeline stage plugins which transform or pre-process data being passed through PEDASI.
    """
    #: Help string to be shown when a user is building a pipeline
    description = 'Does nothing'

    def transform(self, data: typing.Mapping) -> typing.Mapping:
        return data
