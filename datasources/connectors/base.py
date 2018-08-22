import abc
import typing


class BaseDataConnector(abc.ABC):
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

    def __init__(self, location):
        self.location = location

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Friendly name of the connector class.
        """
        raise NotImplementedError

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

    @classmethod
    def __enter__(cls, location):
        return cls(location)

    @classmethod
    def __exit__(cls, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def _recurse_subclasses(cls):
        from . import iotuk

        for subclass in cls.__subclasses__():
            yield subclass
            yield from subclass._recurse_subclasses()

    @classmethod
    def get_plugin(cls, name: str):
        """
        Find the plugin matching the requested name.

        :param name: Name of plugin to find
        :return: Plugin class
        """
        subclasses = list(cls._recurse_subclasses())

        for subclass in subclasses:
            if subclass.name == name:
                return subclass


class DataConnectorHasMetaData:
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


class InternalDataConnector(BaseDataConnector):
    """
    Base class of data connectors which provide access to data / metadata stored internally.
    """
