"""
This module contains classes required to build a data pipeline from a series of data connectors.
"""

import typing

from .base import DataSetConnector


# TODO inherit from something above BaseDataConnector - a common interface - and make BDC for the final pipeline stage
class Pipeline(DataSetConnector):
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 metadata: typing.Optional = None):
        super().__init__(location, api_key, auth=auth, metadata=metadata)

        self._terminator = DataSetConnector(location, api_key, auth=auth)
        self._pipeline = []

    def append_stage(self, klass: typing.Type, *args, **kwargs):
        self._pipeline.append(klass(*args, **kwargs))

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        data = self._terminator.get_data(params)

        for stage in self._pipeline:
            data = stage.transform()

        return data
