"""
This module contains base classes for data connectors.

Data connectors are the component of PEDASI which interacts directly with data provider APIs.
"""

import abc
from collections import abc as collections_abc
import typing

import requests
import requests.auth

from core import plugin


class BaseDataConnector(metaclass=plugin.Plugin):
    """
    Base class of data connectors which provide access to data / metadata via an external API.

    DataConnectors may be defined for sources which provide:

    * A single dataset
    * A data catalogue - a collection of datasets
    """
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


class DataSetConnector(BaseDataConnector):
    """
    Base class of data connectors which provide access to a single dataset.
    """
    @abc.abstractmethod
    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get data from this source using the appropriate API.

        :param params: Optional query parameter filters
        :return: Requested data
        """
        raise NotImplementedError


class DataConnectorContainsDatasets:
    """
    Mixin class indicating that the plugin represents a data source containing
    multiple datasets.
    """
    @abc.abstractmethod
    def get_datasets(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get the list of all dataset identifiers contained within this source
        using the appropriate API.

        :param params: Optional query parameter filters
        :return: All dataset identifiers
        """
        raise NotImplementedError


class DataConnectorHasMetadata:
    """
    Mixin class indicating the the plugin represents a data source with metadata.
    """
    @abc.abstractmethod
    def get_metadata(self,
                     dataset: typing.Optional[str] = None,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get metadata from this source using the appropriate API.

        :param dataset: Optional dataset for which to get metadata
        :param params: Optional query parameter filters
        :return: Requested metadata
        """
        raise NotImplementedError
