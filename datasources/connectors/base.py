import abc
import typing


from pedasi.common import plugin


class BaseDataConnector(metaclass=plugin.Plugin):
    """
    Base class of data connectors which provide access to data / metadata via an external API.

    DataConnectors may be defined for sources which provide:

    * A single dataset
    * A data catalogue - a collection of datasets

    TODO:

    * Should this connector interface be able to handle data catalogues and datasets
      or should we create a new connector for datasets within a catalogue?
    * What other operations do we need?
    """
    def __init__(self, location: str,
                 api_key: typing.Optional[str] = None):
        self.location = location
        self.api_key = api_key

    @abc.abstractmethod
    def get_data(self,
                 dataset: typing.Optional[str] = None,
                 query_params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get data from this source using the appropriate API.

        :param dataset: Optional dataset for which to get data
        :param query_params: Optional query parameter filters
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
                     query_params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get the list of all dataset identifiers contained within this source
        using the appropriate API.

        :param query_params: Optional query parameter filters
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
                     query_params: typing.Optional[typing.Mapping[str, str]] = None):
        """
        Get metadata from this source using the appropriate API.

        :param dataset: Optional dataset for which to get metadata
        :param query_params: Optional query parameter filters
        :return: Requested metadata
        """
        raise NotImplementedError
