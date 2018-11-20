"""
This module contains functionality for configurable plugins.
"""

import abc
import importlib
import typing
import pathlib

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

    def get_plugin(cls, class_name: str) -> typing.Type:
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

    @property
    def plugin_choices(cls) -> typing.List[typing.Tuple[str, str]]:
        return [(name, name) for name, plugin in cls._plugins.items()]
