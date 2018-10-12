"""
This module contains the data connector for IoTUK Nations.
"""
import typing

import requests

from .base import DataSetConnector


class IoTUK(DataSetConnector):
    """
    Data connector for retrieving data from IoTUK Nations.
    """
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
        response = requests.get(self.location, params=params)
        return response.json()
