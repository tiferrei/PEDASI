"""
This module contains base classes for data connectors.

Data connectors are the component of PEDASI which interacts directly with data provider APIs.
"""

import abc
from collections import abc as collections_abc
import enum
import typing

import requests
import requests.auth

from core import plugin


class ConnectorType(enum.IntEnum):
    CATALOGUE = 1
    DATASET = 2


class BaseDataConnector(metaclass=plugin.Plugin):
    """
    Base class of data connectors which provide access to data / metadata via an external API.

    DataConnectors may be defined for sources which provide:

    * A single dataset
    * A data catalogue - a collection of datasets
    """
    TYPE = None

    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 **kwargs):
        self.location = location
        self.api_key = api_key

    @abc.abstractmethod
    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get metadata from this source using the appropriate API.

        :param params: Optional query parameter filters
        :return: Requested metadata
        """
        raise NotImplementedError

    def _get_auth_request(self, url, **kwargs):
        return requests.get(url,
                            auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
                            **kwargs)


class DataCatalogueConnector(BaseDataConnector, collections_abc.Mapping):
    """
    Base class of data connectors which provide access to a data catalogue.
    """
    TYPE = ConnectorType.CATALOGUE

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        raise TypeError('Data catalogues contain only metadata.  You must select a dataset.')

    @abc.abstractmethod
    def get_datasets(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None) -> typing.List[str]:
        """
        Get the list of datasets provided by this catalogue.

        :param params: Query parameters to pass to data source API
        :return: List of datasets provided by this catalogue
        """

    def __iter__(self):
        return iter(self.get_datasets())

    def __len__(self):
        return len(self.get_datasets())


class DataSetConnector(BaseDataConnector):
    """
    Base class of data connectors which provide access to a single dataset.
    """
    TYPE = ConnectorType.DATASET

    @abc.abstractmethod
    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get data from this source using the appropriate API.

        :param params: Optional query parameter filters
        :return: Requested data
        """
        raise NotImplementedError
