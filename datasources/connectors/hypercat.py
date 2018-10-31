"""
This module contains data connector classes for retrieving data from HyperCat catalogues.
"""

import typing

from .base import BaseDataConnector, DataCatalogueConnector, DataSetConnector


class HyperCat(DataCatalogueConnector):
    """
    Data connector for retrieving data or metadata from a HyperCat catalogue.
    """
    dataset_connector_class = DataSetConnector

    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None):
        super().__init__(location, api_key=api_key, auth=auth)

        self._response = None

    def __getitem__(self, item: str) -> BaseDataConnector:
        params = {
            'href': item
        }

        response = self._get_response(params)

        dataset_item = self._get_item_by_key_value(
            response['items'],
            'href',
            item
        )
        metadata = dataset_item['item-metadata']

        try:
            try:
                content_type = self._get_item_by_key_value(
                    metadata,
                    'rel',
                    'urn:X-hypercat:rels:isContentType'
                )['val']

            except KeyError:
                content_type = self._get_item_by_key_value(
                    metadata,
                    'rel',
                    'urn:X-hypercat:rels:containsContentType'
                )['val']

            if content_type == 'application/vnd.hypercat.catalogue+json':
                return type(self)(location=item,
                                  api_key=self.api_key,
                                  auth=self.auth)

        except (KeyError, ValueError):
            # Has no or multiple values for content type - is not a catalogue
            pass

        return self.dataset_connector_class(item, self.api_key,
                                            auth=self.auth,
                                            metadata=metadata)

    def items(self,
              params=None) -> typing.ItemsView:
        """
        Get key-value pairs of dataset ID to dataset connector for datasets contained within this catalogue.

        :param params: Query parameters to be passed through to the data source API
        :return: Dictionary ItemsView over datasets
        """
        response = self._get_response(params)

        return {
            item['href']: self.dataset_connector_class(item['href'], self.api_key,
                                                       auth=self.auth,
                                                       metadata=item['item-metadata'])
            for item in response['items']
        }.items()

    # TODO this gets the entire HyperCat contents so is slow on the BT HyperCat API - ~1s
    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        response = self._get_response(params)

        return response['catalogue-metadata']

    def get_datasets(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.List[str]:
        response = self._get_response(params=params)

        datasets = []
        for item in response['items']:
            datasets.append(item['href'])

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
        self._response = self._get_auth_request(self.location)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
