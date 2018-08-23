import typing

import requests

from datasources.connectors.base import BaseDataConnector, DataConnectorContainsDatasets, DataConnectorHasMetadata


class HyperCat(DataConnectorContainsDatasets, DataConnectorHasMetadata, BaseDataConnector):
    name = 'HyperCat'

    def get_data(self,
                 dataset: typing.Optional[str] = None,
                 query_params: typing.Optional[typing.Mapping[str, str]] = None):
        super().get_data(dataset, query_params)

    def get_datasets(self,
                     query_params: typing.Optional[typing.Mapping[str, str]] = None):
        return [item['href'] for item in self.response['items']]

    def get_metadata(self,
                     dataset: typing.Optional[str] = None,
                     query_params: typing.Optional[typing.Mapping[str, str]] = None):
        if dataset is None:
            metadata = self.response['catalogue-metadata']
            metadata_dict = {}
            for item in metadata:
                relation = item['rel']
                value = item['val']

                if relation not in metadata_dict:
                    metadata_dict[relation] = []
                metadata_dict[relation].append(value)

        else:
            dataset_item = self._get_item_by_key_value(
                self.response['items'],
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
    def _get_item_by_key_value(collection: typing.Iterable[typing.Mapping[str, str]],
                               key: str, value: str) -> typing.List[typing.Mapping[str, str]]:
        vals = []
        for item in collection:
            if item[key] == value:
                vals.append(item)

        if not vals:
            raise KeyError
        if len(vals) == 1:
            vals = vals[0]

        return vals

    def __enter__(self):
        r = requests.get(self.location)
        self.response = r.json()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
