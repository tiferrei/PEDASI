"""
This module contains base classes for data connectors.

Data connectors are the component of PEDASI which interacts directly with data provider APIs.
"""

import abc
from collections import abc as collections_abc
from collections import OrderedDict
import enum
import typing

import requests
import requests.auth

from core import plugin


@enum.unique
class AuthMethod(enum.IntEnum):
    """
    Authentication method to be used when performing a request to the external API.
    """
    # Does not require authentication
    NONE = -1

    # Unknown - assume no authentication if a request is sent
    UNKNOWN = 0

    # HTTPBasicAuth from Requests
    BASIC = 1

    # Same as HTTPBasicAuth but key is already b64 encoded
    HEADER = 2

    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)


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


class RequestCounter:
    def __init__(self, count: int = 0):
        self._count = count

    def __iadd__(self, other: int):
        self._count += other
        return self

    def count(self):
        return self._count


class BaseDataConnector(metaclass=plugin.Plugin):
    """
    Base class of data connectors which provide access to data / metadata via an external API.

    DataConnectors may be defined for sources which provide:

    * A single dataset
    * A data catalogue - a collection of datasets
    """
    #: Does this data connector represent a data catalogue containing multiple datasets?
    is_catalogue = None

    #: Help string to be shown when a data provider is choosing a connector
    description = None

    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 **kwargs):
        self.location = location
        self.api_key = api_key
        self.auth = auth

        self._request_counter = RequestCounter()

    @property
    def request_count(self):
        return self._request_counter.count()

    # TODO make normal method
    @staticmethod
    def determine_auth_method(url: str, api_key: str) -> AuthMethod:
        """
        Determine which authentication method to use to access the data source.

        Test each known authentication method in turn until one succeeds.

        :param url: URL to authenticate against
        :param api_key: API key to use for authentication
        :return: First successful authentication method
        """
        # If not using an API key - can't require auth
        if not api_key:
            return AuthMethod.NONE

        for auth_method_id, auth_function in REQUEST_AUTH_FUNCTIONS.items():
            try:
                # Can we get a response using this auth method?
                if auth_function is None:
                    response = requests.get(url)

                else:
                    response = requests.get(url,
                                            auth=auth_function(api_key, ''))

                response.raise_for_status()
                return auth_method_id

            except requests.exceptions.HTTPError:
                pass

        # None of the attempted authentication methods was successful
        raise requests.exceptions.ConnectionError('Could not authenticate against external API')

    def get_metadata(self,
                     params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get metadata from this source using the appropriate API.

        :param params: Optional query parameter filters
        :return: Requested metadata
        """
        try:
            if self._metadata is not None:
                return self._metadata

        except AttributeError:
            pass

        raise NotImplementedError('This data connector does not provide metadata')

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
        self._request_counter += 1

        if self.auth is None:
            return requests.get(url, **kwargs)

        return requests.get(url,
                            auth=self.auth(self.api_key, ''),
                            **kwargs)


class ReadOnlyInternalDataConnector(abc.ABC):
    """
    Abstract mixin representing a connector for an internally hosted data source which is read only.
    """
    @abc.abstractmethod
    def clean_data(self, **kwargs):
        """
        Clean, validate or otherwise structure the data contained within this data source.
        """
        raise NotImplementedError


class InternalDataConnector(ReadOnlyInternalDataConnector):
    """
    Abstract mixin representing a connector for an internally hosted data source which is able to be written to.
    """
    @abc.abstractmethod
    def clear_data(self):
        """
        Clear all data from this data source.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def post_data(self, data: typing.Union[typing.MutableMapping[str, str],
                                           typing.List[typing.MutableMapping[str, str]]]):
        """
        Add data to this data source.

        :param data: Data to add
        """
        raise NotImplementedError


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
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, item: str) -> BaseDataConnector:
        raise NotImplementedError

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

    #: Help string to be shown when a data provider is choosing a connector
    description = (
        'This connector is the default option and should be used when accessing an API at a single endpoint '
        'which may or may not accept query parameters.'
    )

    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None,
                 auth: typing.Optional[typing.Callable] = None,
                 metadata: typing.Optional = None):
        super().__init__(location, api_key, auth=auth)

        self._metadata = metadata

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

        if 'json' in response.headers['Content-Type']:
            return response.json()

        return response.text
