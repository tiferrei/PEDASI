"""
This module contains data connector classes for retrieving data from HyperCat catalogues.
"""

import typing

import requests
import requests.auth

from datasources.connectors.base import BaseDataConnector, DataCatalogueConnector, DataSetConnector


class HyperCatDataSetConnector(DataSetConnector):
    """
    Data connector for retrieving data from a source contained within a HyperCat catalogue.

    Metadata is assumed to be given by the parent catalogue.
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 metadata: typing.Optional[typing.Mapping] = None):
        super().__init__(location, api_key)

        self._metadata = metadata

    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Retrieve the metadata for this source.

        The metadata must have been given when this data source was looked up in the
        parent catalogue.

        :param params: Ignored
        :return: Data source metadata
        """
        if self._metadata is None:
            raise NotImplementedError

        return self._metadata

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.Union[str, dict]:
        """
        Retrieve the data from this source.

        If the data is JSON formatted it will be parsed into a dictionary - otherwise it will
        be passed as plain text.

        :param params: Query parameters to be passed through to the data source API
        :return: Data source data
        """
        response = self.get_data_passthrough(params)

        if 'json' in response.headers['Content-Type']:
            return response.json()

        return response.text

    def get_data_passthrough(self,
                             params: typing.Optional[typing.Mapping[str, str]] = None) -> requests.Response:
        """
        Retrieve the data from this source.

        The response from the data source API will be returned directly.

        :param params: Query parameters to be passed through to the data source API
        :return: Data source data
        """
        response = self._get_auth_request(self.location,
                                          params=params)
        response.raise_for_status()
        return response


class CiscoHyperCatDataSetConnector(HyperCatDataSetConnector):
    """
    Data connector behaving the same as :class:`HyperCatDataSetConnector` with authentication
    for Cisco HyperCat API.
    """
    def _get_auth_request(self, url: str, **kwargs) -> requests.Response:
        """
        Perform an API request with authentication by API key.

        :param url: URL to query
        :return: Request response
        """
        return requests.get(url,
                            # Doesn't accept HttpBasicAuth
                            headers={'Authorization': self.api_key},
                            **kwargs)


class HyperCat(DataCatalogueConnector):
    """
    Data connector for retrieving data or metadata from a HyperCat catalogue.
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None):
        super().__init__(location, api_key=api_key)

        self._response = None

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, item: str) -> BaseDataConnector:
        params = {
            'href': item
        }

        # Use cached response if we have one
        # TODO should we use cached responses?
        response = self._response
        if response is None:
            response = self._get_response(params)

        dataset_item = self._get_item_by_key_value(
            response['items'],
            'href',
            item
        )
        metadata = dataset_item['item-metadata']

        try:
            content_type = self._get_item_by_key_value(
                metadata,
                'rel',
                'urn:X-hypercat:rels:isContentType'
            )['val']

            if content_type == 'application/vnd.hypercat.catalogue+json':
                return type(self)(location=item,
                                  api_key=self.api_key)

        except ValueError:
            # Has multiple values for content type - is not a catalogue
            pass

        return HyperCatDataSetConnector(item, self.api_key,
                                        metadata=metadata)

    # TODO should this be able to return metadata for multiple datasets at once?
    # TODO should there be a different method for getting catalogue metadata?
    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        # Use cached response if we have one
        response = self._response
        if response is None:
            response = self._get_response(params)

        return response['catalogue-metadata']

    def get_datasets(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.List[str]:
        response = self._response
        if response is None:
            response = self._get_response(params=params)

        datasets = {}
        for item in response['items']:
            href = item['href']

            try:
                name = self._get_item_by_key_value(
                    item['item-metadata'],
                    'rel',
                    'urn:X-bt:rels:feedTitle'
                )['val']

            except KeyError:
                name = None

            datasets[href] = name

        return datasets

    @staticmethod
    def _get_item_by_key_value(collection: typing.Iterable[typing.Mapping],
                               key: str, value: typing.Any) -> typing.Mapping:
        matches = [item for item in collection if item[key] == value]

        if not matches:
            raise KeyError
        elif len(matches) > 1:
            raise ValueError('Multiple items were found')

        return matches[0]

    def _get_response(self, params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.Mapping:
        response = self._get_auth_request(self.location,
                                          params=params)
        response.raise_for_status()
        return response.json()

    def __enter__(self):
        self._response = self._get_response()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


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

    def __iter__(self):
        return iter(self.get_datasets())

    def __len__(self):
        raise NotImplementedError

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

        return CiscoEntityConnector(item, self.api_key,
                                    metadata=dataset_item)

    # TODO should this be able to return metadata for multiple datasets at once?
    # TODO should there be a different method for getting catalogue metadata?
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


class HyperCatCisco(HyperCat):
    """
    Data connector for retrieving data or metadata from a HyperCat catalogue.

    This connector is designed to handle the structure of Cisco's HyperCat and Entity APIs.
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 entity_url: str = None):
        super().__init__(location, api_key=api_key)

        self.entity_url = entity_url

    def __getitem__(self, item):
        params = {
            'href': item
        }

        # Use cached response if we have one
        response = self._response
        if response is None:
            response = self._get_response(params)

        dataset_item = self._get_item_by_key_value(
            response['items'],
            'href',
            item
        )
        metadata = dataset_item['item-metadata']

        try:
            content_type = self._get_item_by_key_value(metadata,
                                                       'rel',
                                                       'urn:X-hypercat:rels:isContentType')['val']

        except KeyError:
            try:
                content_type = self._get_item_by_key_value(
                    metadata,
                    'rel',
                    'urn:X-hypercat:rels:containsContentType'
                )['val']

            except KeyError:
                content_type = None

        except ValueError:
            # Had multiple content types - is not a catalogue
            content_type = None

        if content_type == 'application/vnd.hypercat.catalogue+json':
            return CiscoEntityConnector(
                location=self._get_item_by_key_value(metadata,
                                                     'rel',
                                                     'urn:X-hypercat:rels:hasHomepage')['val'],
                api_key=self.api_key,
                metadata=metadata)

        return HyperCatDataSetConnector(item, self.api_key,
                                        metadata=metadata)

    def _get_auth_request(self, url, **kwargs):
        return requests.get(url,
                            # Doesn't accept HttpBasicAuth
                            headers={'Authorization': self.api_key},
                            **kwargs)
