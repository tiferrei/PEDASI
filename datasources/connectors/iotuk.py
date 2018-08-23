import typing

import requests

from .base import BaseDataConnector


class IoTUK(BaseDataConnector):
    def get_data(self,
                 dataset: typing.Optional[str] = None,
                 query_params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get data from a source using the IoTUK Nation API.

        :param dataset: Optional dataset for which to get data
        :param query_params: Optional query parameter filters
        :return: Requested data
        """
        r = requests.get(self.location, params=query_params)
        return r.json()
