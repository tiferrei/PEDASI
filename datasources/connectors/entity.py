
import typing

import requests
import requests.auth

from .base import BaseDataConnector, DataCatalogueConnector
from .passthrough import CiscoHyperCatDataSetConnector


class CiscoEntityConnector(DataCatalogueConnector):
    """
    Data connector for retrieving data or metadata from Cisco's Entity API.
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 metadata: typing.Optional[typing.Mapping] = None):
        super().__init__(location, api_key=api_key)

        self._response = None
        self._metadata = metadata

    def __getitem__(self, item: str) -> BaseDataConnector:
        params = {
            'href': item
        }

        # Use cached response if we have one
        response = self._response
        if response is None:
            response = self._get_response(params=params)

        dataset_item = self._get_item_by_key_value(
            response,
            'uri',
            item
        )

        if 'timeseries' in item:
            return CiscoHyperCatDataSetConnector(item, self.api_key,
                                                 metadata=dataset_item)

        return type(self)(item, self.api_key,
                          metadata=dataset_item)

    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        if self._metadata is None:
            raise NotImplementedError

        return self._metadata

    def get_datasets(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.List[str]:
        # Use cached response if we have one
        response = self._response
        if response is None:
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

    def _get_response(self, params: typing.Optional[typing.Mapping[str, str]] = None):
        response = self._get_auth_request(self.location,
                                          params=params)
        response.raise_for_status()
        return response.json()

    def _get_auth_request(self, url, **kwargs):
        return requests.get(url,
                            # Doesn't accept HttpBasicAuth
                            headers={'Authorization': self.api_key},
                            **kwargs)

    def __enter__(self):
        self._response = self._get_response()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

