import typing

import requests
import requests.auth

from datasources.connectors.base import DataCatalogueConnector, DataSetConnector


class HyperCatDataSetConnector(DataSetConnector):
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 metadata: typing.Optional[typing.Mapping] = None):
        super().__init__(location, api_key)

        self._metadata = metadata

    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        return self._metadata

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        r = self.get_data_passthrough(params)

        if r.headers['Content-Type'] == 'application/json':
            return r.json()

        return r.text

    def get_data_passthrough(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        r = requests.get(self.location,
                         params=params,
                         auth=requests.auth.HTTPBasicAuth(self.api_key, ''))
        r.raise_for_status()
        return r


class HyperCat(DataCatalogueConnector):
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None):
        super().__init__(location, api_key=api_key)

        self._response = None

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

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

        content_type = self._get_item_by_key_value(metadata, 'rel', 'urn:X-hypercat:rels:isContentType')['val']
        if content_type == 'application/vnd.hypercat.catalogue+json':
            return type(self)(location=item,
                              api_key=self.api_key)
        else:
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
