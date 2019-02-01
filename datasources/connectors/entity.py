"""
This module contains connectors for receiving data via Cisco's Entity API.
"""

import typing

from .base import BaseDataConnector, DataCatalogueConnector, DataSetConnector


class CiscoEntityConnector(DataCatalogueConnector):
    """
    Data connector for retrieving data or metadata from Cisco's Entity API.
    """
    dataset_connector_class = DataSetConnector

    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 metadata: typing.Optional[typing.Mapping] = None):
        super().__init__(location, api_key=api_key, auth=auth)

        self._response = None
        self._metadata = metadata

    def __getitem__(self, item: str) -> BaseDataConnector:
        params = {
            'href': item
        }

        # Use cached response if we have one
        response = self._get_response(params=params)

        dataset_item = self._get_item_by_key_value(
            response,
            'uri',
            item
        )

        if 'timeseries' in item:
            return self.dataset_connector_class(item, self.api_key,
                                                auth=self.auth,
                                                metadata=dataset_item)

        return type(self)(item, self.api_key,
                          auth=self.auth,
                          metadata=dataset_item)

    def items(self,
              params=None) -> typing.ItemsView:
        """
        Get key-value pairs of dataset ID to dataset connector for datasets contained within this catalogue.

        :param params: Query parameters to be passed through to the data source API
        :return: Dictionary ItemsView over datasets
        """
        # Use cached response if we have one
        response = self._get_response(params)

        connector_dict = {
            item['uri']: self.dataset_connector_class(item['uri'], self.api_key,
                                                      auth=self.auth,
                                                      metadata=item)
            # Response JSON is a list of entities
            for item in response
        }

        return connector_dict.items()

    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        if self._metadata is None:
            raise NotImplementedError

        return self._metadata

    def get_datasets(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.List[str]:
        # Use cached response if we have one
        response = self._get_response(params=params)

        datasets = []
        if len(response) == 1 and 'timeseries' in response[0]:
            # Response is one entity which should contain data series?
            # TODO is it always 'timeseries'?
            for item in response[0]['timeseries']:
                datasets.append(item['uri'])

        else:
            for item in response:
                datasets.append(item['uri'])

        return datasets

    @staticmethod
    def _get_item_by_key_value(collection: typing.Iterable[typing.Mapping],
                               key: str, value) -> typing.Mapping:
        matches = [item for item in collection if item[key] == value]

        if not matches:
            raise KeyError
        elif len(matches) > 1:
            raise ValueError('Multiple items were found')

        return matches[0]

    def _get_response(self, params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.Mapping:
        # Use cached response if we have one
        # TODO should we use cached responses?
        if self._response is not None and params is None:
            # Ignore params - they only filter - we already have everything
            response = self._response
        else:
            response = self._get_auth_request(self.location,
                                              params=params)
        response.raise_for_status()
        return response.json()

    def __enter__(self):
        self._response = self._get_response()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
