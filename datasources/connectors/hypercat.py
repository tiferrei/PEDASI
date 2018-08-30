import typing

import requests

from datasources.connectors.base import BaseDataConnector, DataConnectorContainsDatasets, DataConnectorHasMetadata


class HyperCat(DataConnectorContainsDatasets, DataConnectorHasMetadata, BaseDataConnector):
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None):
        super().__init__(location, api_key=api_key)

        self._response = None

    def get_data(self,
                 dataset: typing.Optional[str] = None,
                 query_params: typing.Optional[typing.Mapping[str, str]] = None):
        super().get_data(dataset, query_params)

    def get_datasets(self,
                     query_params: typing.Optional[typing.Mapping[str, str]] = None):
        response = self._response
        if response is None:
            response = self._get_response(query_params)

        return [item['href'] for item in response['items']]

    # TODO should this be able to return metadata for multiple datasets at once?
    # TODO should there be a different method for getting catalogue metadata?
    def get_metadata(self,
                     dataset: typing.Optional[str] = None,
                     query_params: typing.Optional[typing.Mapping[str, str]] = None):
        if query_params is None:
            query_params = {}

        if dataset is not None:
            # Copy so we can update without side effect
            query_params = dict(query_params)
            query_params['href'] = dataset

        # Use cached response if we have one
        response = self._response
        if response is None:
            response = self._get_response(query_params)

        if dataset is None:
            metadata = response['catalogue-metadata']

        else:
            dataset_item = self._get_item_by_key_value(
                response['items'],
                'href',
                dataset
            )
            metadata = dataset_item['item-metadata']

        metadata_dict = {}
        for item in metadata:
            relation = item['rel']
            value = item['val']

            if relation not in metadata_dict:
                metadata_dict[relation] = []
            metadata_dict[relation].append(value)

        return metadata_dict

    @staticmethod
    def _get_item_by_key_value(collection: typing.Iterable[typing.Mapping],
                                key: str, value) -> typing.Mapping:
        matches = [item for item in collection if item[key] == value]

        if not matches:
            raise KeyError
        elif len(matches) > 1:
            raise ValueError('Multiple items were found')

        return matches[0]

    def _get_response(self, query_params: typing.Optional[typing.Mapping[str, str]] = None):
        r = requests.get(self.location, params=query_params)
        return r.json()

    def __enter__(self):
        self._response = self._get_response()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
