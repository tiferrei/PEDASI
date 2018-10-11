import typing

import requests
import requests.auth

from datasources.connectors.base import BaseDataConnector, DataConnectorContainsDatasets, DataConnectorHasMetadata


class HyperCat(DataConnectorContainsDatasets, DataConnectorHasMetadata, BaseDataConnector):
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None):
        super().__init__(location, api_key=api_key)

        self._response = None

    def get_data(self,
                 dataset: typing.Optional[str] = None,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        r = self.get_data_passthrough(dataset=dataset,
                                      params=params)
        return r.text

    def get_data_passthrough(self,
                 dataset: typing.Optional[str] = None,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        if dataset is None:
            raise ValueError('When requesting data from a HyperCat catalogue you must provide a dataset href.')

        location = dataset
        r = requests.get(location,
                         params=params,
                         auth=requests.auth.HTTPBasicAuth(self.api_key, ''))
        r.raise_for_status()
        return r

    def get_datasets(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
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

    # TODO should this be able to return metadata for multiple datasets at once?
    # TODO should there be a different method for getting catalogue metadata?
    def get_metadata(self,
                     dataset: typing.Optional[str] = None,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        if params is None:
            params = {}

        if dataset is None:
            # Query parameter href refers to a single dataset
            try:
                dataset = params['href']
            except KeyError:
                pass

        else:
            # Copy so we can update without side effect
            params = dict(params)
            params['href'] = dataset

        # Use cached response if we have one
        response = self._response
        if response is None:
            response = self._get_response(params)

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

    def _get_response(self, params: typing.Optional[typing.Mapping[str, str]] = None):
        r = self._get_auth_request(self.location,
                                   params=params)
        r.raise_for_status()
        return r.json()

    def _get_auth_request(self, url, **kwargs):
        return requests.get(url,
                            auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                            **kwargs)

    def __enter__(self):
        self._response = self._get_response()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class HyperCatCisco(HyperCat):
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 entity_url: str = None):
        super().__init__(location, api_key=api_key)

        self.entity_url = entity_url

    def get_entities(self):
        r = self._get_auth_request(self.entity_url)
        return r.json()

    def _get_auth_request(self, url, **kwargs):
        return requests.get(url,
                            # Doesn't accept HttpBasicAuth
                            headers={'Authorization': self.api_key},
                            **kwargs)
