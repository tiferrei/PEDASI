import abc
import importlib
import pathlib
import typing

from django.conf import settings


class Plugin(abc.ABCMeta):
    """
    Metaclass for plugin components.

    The base class for each type of plugin should use this metaclass.
    """
    def __init__(cls, name, bases, attrs):
        """
        Metaclass initialiser - called when a new class is defined.

        When a new class is defined it will be registered as an available plugin.

        :param name: Name of the new class
        :param bases: Base classes of the new class
        :param attrs: Attributes of the new class
        """
        super().__init__(name, bases, attrs)

        if not hasattr(cls, '_plugins'):
            cls._plugins = {}
        else:
            cls._plugins[name] = cls

    def get_plugin(cls, class_name: str) -> type:
        """
        Get a plugin class by name.

        :param class_name: Name of plugin class
        :return: Plugin class
        """
        return cls._plugins[class_name]

    @staticmethod
    def load_plugins(plugin_dir: typing.Union[str, pathlib.Path]) -> None:
        """
        Load plugins from plugin directory.

        :param plugin_dir: Directory to search for plugins
        """
        full_plugin_path = pathlib.Path(settings.BASE_DIR).joinpath(plugin_dir)

        for plugin_filename in full_plugin_path.iterdir():
            module_name = plugin_filename.stem
            if plugin_filename.suffix != '.py' or module_name in {'__init__', 'base'}:
                continue

            # When importing a module the class definitions are executed
            # This causes a call to the metaclass __init__ method which registers the plugin
            importlib.import_module(str(plugin_dir).replace('/', '.') + '.' + module_name)


class BaseDataConnector(metaclass=Plugin):
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


class DataConnectorHasMetadata:
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
