import typing

import requests

from .base import DataSetConnector


class IoTUK(DataSetConnector):
    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        raise NotImplementedError('IoTUK does not provide metadata')

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get data from a source using the IoTUK Nation API.

        :param params: Optional query parameter filters
        :return: Requested data
        """
        r = requests.get(self.location, params=params)
        return r.json()
