"""
This module contains a data connector class for retrieving data via a REST API.
"""

import typing
import urllib.parse

from .base import BaseDataConnector, DataCatalogueConnector


class RestApiConnector(DataCatalogueConnector):
    """
    Data connector for retrieving data from a REST API.
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None):
        super().__init__(location, api_key=api_key, auth=auth)

        self._response = None

    def __getitem__(self, item: str) -> BaseDataConnector:
        url = urllib.parse.urljoin(self.location, item)

        return type(self)(location=url,
                          api_key=self.api_key,
                          auth=self.auth)

    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Metadata is not supported by this connector.
        """
        raise NotImplementedError('This data connector does not provide metadata')

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Retrieve the data from this source.

        If the data is JSON formatted it will be parsed into a dictionary - otherwise it will
        be passed as plain text.

        :param params: Query parameters to be passed through to the data source API
        :return: Data source data
        """
        response = self.get_response(params)

        if 'json' in response.headers['Content-Type']:
            return response.json()

        return response.text

    def get_datasets(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.List[str]:
        """
        Listing datasets is not supported by this connector.
        """
        raise NotImplementedError('This data connector does not provide a list of datasets')

    def __enter__(self):
        self._response = self._get_auth_request(self.location)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
