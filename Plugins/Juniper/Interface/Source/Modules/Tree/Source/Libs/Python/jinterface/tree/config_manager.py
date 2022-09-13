import os
import functools

import juniper.engine
import juniper.types.framework.singleton
import juniper.engine.types.plugin
import juniper.paths
import juniper.utilities.json as json_utils


class ConfigManager(object, metaclass=juniper.types.framework.singleton.Singleton):

    def __init__(self):
        pass

    @property
    @functools.lru_cache()
    def config_path(self):
        """Gets the juniper_tree.json path for juniper tree"""
        tree_plugin = None
        for i in juniper.engine.JuniperEngine().modules:
            if(type(i).__name__ == "Tree"):
                tree_plugin = i
        return os.path.join(
            tree_plugin.root,
            "Config\\juniper_tree.json"
        )

    def __get_config_property(self, property):
        """Gets a property from a config file
        :param <str:property> Can be a single key, or a nested key (Ie, "instance.button.width"")
        :return <value:value> The value as retrieved from the config
        """
        return json_utils.get_property(self.config_path, property)

    @property
    def button_height(self):
        return self.__get_config_property("ui.button.height")

    @property
    def default_width(self):
        return self.__get_config_property("ui.default_width")

    @property
    def default_columns(self):
        return self.__get_config_property("ui.default_columns")
