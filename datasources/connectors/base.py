"""
This module contains base classes for data connectors.

Data connectors are the component of PEDASI which interacts directly with data provider APIs.
"""

import abc
from collections import abc as collections_abc
from collections import OrderedDict
import enum
import json
import typing

import requests
import requests.auth

from core import plugin


@enum.unique
class AuthMethod(enum.Enum):
    NONE = -1
    UNKNOWN = 0
    BASIC = 1
    HEADER = 2

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class HttpHeaderAuth(requests.auth.HTTPBasicAuth):
    """
    Requests Auth provider.

    The same as HttpBasicAuth - but don't convert to base64

    Used for e.g. Cisco HyperCat API
    """
    def __call__(self, r):
        r.headers['Authorization'] = self.username
        return r


REQUEST_AUTH_FUNCTIONS = OrderedDict([
    (AuthMethod.NONE, None),
    (AuthMethod.UNKNOWN, None),
    (AuthMethod.BASIC, requests.auth.HTTPBasicAuth),
    (AuthMethod.HEADER, HttpHeaderAuth),
])


class DummyRequestsResponse:
    def __init__(self,
                 text: str,
                 status_code: int,
                 content_type: str):
        self.text = text
        self.status_code = status_code
        self.headers = {
            'content-type': content_type,
            'Content-Type': content_type,
        }

    def json(self):
        return json.loads(self.text)


class BaseDataConnector(metaclass=plugin.Plugin):
    """
    Base class of data connectors which provide access to data / metadata via an external API.

    DataConnectors may be defined for sources which provide:

    * A single dataset
    * A data catalogue - a collection of datasets
    """
    #: Does this data connector represent a data catalogue containing multiple datasets?
    is_catalogue = None

    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 **kwargs):
        self.location = location
        self.api_key = api_key
        self.auth = auth

    @abc.abstractmethod
    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get metadata from this source using the appropriate API.

        :param params: Optional query parameter filters
        :return: Requested metadata
        """
        raise NotImplementedError

    def get_response(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Transparently return a response from a source API.

        :param params: Optional query parameter filters
        :return: Requested data / metadata - response is passed transparently
        """
        return self._get_auth_request(self.location,
                                      params=params)

    def _get_auth_request(self, url, **kwargs):
        if self.auth is None:
            return requests.get(url, **kwargs)

        return requests.get(url,
                            auth=self.auth(self.api_key, ''),
                            **kwargs)


class DataCatalogueConnector(BaseDataConnector, collections_abc.Mapping):
    """
    Base class of data connectors which provide access to a data catalogue.
    """
    #: Does this data connector represent a data catalogue containing multiple datasets?
    is_catalogue = True

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

    Metadata may be passed to the constructor if it has been collected from a previous source
    otherwise attempting to retrieve metadata will raise NotImplementedError.

    If you wish to connect to a source that provides metadata itself, you must create a new
    connector class which inherits from this one.
    """
    #: Does this data connector represent a data catalogue containing multiple datasets?
    is_catalogue = False

    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 metadata: typing.Optional = None):
        super().__init__(location, api_key, auth=auth)

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
            raise NotImplementedError('This data connector does not provide metadata')

        return self._metadata

    def get_data(self,
                 params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Retrieve the data from this source.

        If the data is JSON formatted it will be parsed into a dictionary - otherwise it will
        be passed as plain text.

        :param params: Query parameters to be passed through to the data source API
        :return: Data source data
        """
        response = self.get_response(params)

        try:
            return response.json()

        except (AttributeError, json.decoder.JSONDecodeError):
            pass

        return response.text
