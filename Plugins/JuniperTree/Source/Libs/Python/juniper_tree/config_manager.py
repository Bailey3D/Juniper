import functools
import os

import juniper.framework.backend.plugin
import juniper.paths
import juniper.utilities.json as json_utils



class __ConfigManager(object):
    __instance__ = None

    def __init__(self):
        pass

    @property
    @functools.lru_cache()
    def config_path(self):
        """Gets the juniper_tree.json path for juniper tree"""
        return os.path.join(
            juniper.framework.backend.plugin.PluginManager().find_plugin("juniper_tree").root,
            "Config\\juniper_tree.json"
        )
        #return juniper.paths.get_config("juniper_tree.json", module="juniper_tree")

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


if(not __ConfigManager.__instance__):
    __ConfigManager.__instance__ = __ConfigManager()
ConfigManager = __ConfigManager.__instance__
