import os
import functools
import json

import juniper.types.framework.singleton
import juniper.paths
import juniper.plugins
import juniper.utilities.string as string_utils
from juniper.utilities import script_execution


class ScriptManager(object, metaclass=juniper.types.framework.singleton.Singleton):
    def __init__(self):
        self.registered_macros = []

    def register(self, script):
        if(script not in self.registered_macros):
            self.registered_macros.append(script)

    def unregister(self, script):
        if(script in self.registered_macros):
            self.registered_macros.remove(script)

    def find(self, script_name, plugin_name="juniper"):
        for i in self.registered_macros:
            if(i.name == script_name):
                if(
                    not plugin_name or
                    (plugin_name and i.plugin_name == plugin_name)
                ):
                    return i
        return None

    def run(self, script_name, force=False):
        for i in self.registered_macros:
            if(i.name == script_name):
                i.run
                break

    def __iter__(self):
        for i in self.registered_macros:
            yield i

    def get_all_of_type(self, type_):
        output = []
        type_ = type_.lower()
        for i in self.registered_macros:
            if(i.type == type_):
                output.append(i)
        return output


class Script(object):
    __manager__ = ScriptManager

    def __init__(self, path, plugin_name=None):
        self.__path = path.lower()
        self.plugin_name = plugin_name or "juniper"

    def __new__(cls, path, plugin_name=None):
        for i in cls.__manager__():
            if(i.path == path.lower()):
                return i
        output = super().__new__(cls)
        output.__init__(path, plugin_name=plugin_name)
        cls.__manager__().register(output)
        return output

    def run(self):
        """Runs this script"""
        if(os.path.isfile(self.path)):
            script_execution.run_file(self.path)

    # -------------------------------------------------------------

    @property
    @functools.lru_cache()
    def toolptr_data(self):
        if(self.is_toolptr):
            with open(self.__path, "r") as f:
                return json.load(f)
        return None

    @property
    def is_toolptr(self):
        return self.__path.endswith(".toolptr")

    @property
    @functools.lru_cache()
    def file_metadata(self):
        output = {}
        if(os.path.isfile(self.path)):
            with open(self.path, "r") as f:
                for line in f.readlines():
                    if(line.startswith(":")):
                        key = line.split(" ", 1)[0].lower().lstrip(":")
                        value = line.split(" ", 1)[1].rstrip("\n")
                        if(key in output):
                            output[key] += "\n" + value
                        else:
                            output[key] = value
        return output

    def get_key(self, key):
        key = key.lower()
        if(self.is_toolptr):
            if(key in self.toolptr_data):
                return self.toolptr_data[key]
        if(key in self.file_metadata):
            return self.file_metadata[key]
        return None

    # -------------------------------------------------------------

    @property
    def path(self):
        """
        :return <str:path> The path to this script
        """
        if(self.is_toolptr):
            # TODO! Relative path mapping for toolptr
            return self.toolptr_data["path"]
        return self.__path

    @property
    def file_name(self):
        return os.path.basename(self.path)

    # -------------------------------------------------------------

    @property
    def name(self):
        if(self.get_key("name")):
            return self.get_key("name")
        elif(self.file_name.endswith("__init__.py")):
            return os.path.basename(os.path.dirname(self.path))
        else:
            return self.file_name.split(".")[0]

    @property
    def display_name(self):
        if(self.get_key("display_name")):
            return self.get_key("display_name")
        else:
            return string_utils.snake_to_name(self.name)

    @property
    def tooltip(self):
        return self.get_key("tooltip") or ""

    @property
    def category(self):
        return self.get_key("category") or "Uncategorized"

    @property
    def group(self):
        return self.get_key("group") or ""

    @property
    def description(self):
        return (
            self.get_key("desc") or
            self.get_key("description") or
            self.get_key("summary") or
            ""
        )

    @property
    def summary(self):
        return self.get_key("summary") or ""

    @property
    def type(self):
        return self.get_key("type")

    # -------------------------------------------------------------

    @property
    def supported_hosts(self):
        output = []
        key = self.get_key("supported_hosts")
        if(key):
            for i in key.lstrip("[").rstrip("]").replace(" ", "").split(","):
                output.append(i)
        return output

    @property
    def unsupported_hosts(self):
        output = []
        key = self.get_key("unsupported_hosts")
        if(key):
            for i in key.lstrip("[").rstrip("]").replace(" ", "").split(","):
                output.append(i)
        return output

    @property
    def is_supported_in_current_host(self):
        supported_hosts = self.supported_hosts
        unsupported_hosts = self.unsupported_hosts
        if(not supported_hosts and juniper.program_context not in unsupported_hosts):
            return True
        elif(juniper.program_context in supported_hosts and juniper.program_context not in unsupported_hosts):
            return True
        return False

    # -------------------------------------------------------------

    @property
    def sort_key(self):
        return self.category + "|" + self.display_name

    # -------------------------------------------------------------

    @property
    def icon_path(self):
        """
        Gets the path to the icon metadata key if provided
        :return <str:path> The absolute path - or None
        """
        key = self.get_key("icon")
        if(key):
            possible_path = key.replace("\\\\", "\\")
            if(possible_path):
                return juniper.paths.find_resource(possible_path, plugin=self.plugin_name)
        return None

    @property
    def has_icon(self):
        return self.icon_path and os.path.isfile(self.icon_path)

    def get_icon(self):
        if(self.has_icon):
            from qtpy import QtGui
            return QtGui.QIcon(self.icon_path)
        return None

    # -------------------------------------------------------------

    @property
    def parent_category(self):
        """
        Gets the outer most category for this tool, dependent on its parent plugin integration type
        (Ie, "Juniper" for integrated, or the plugin name for "Standalone" or "Separate")
        :return <str:category> The target category - defaults to "Juniper" if none is set
        """
        if(self.plugin_name):
            target_plugin = juniper.plugins.PluginManager().find_plugin(self.plugin_name)
            if(target_plugin and target_plugin.integration_type in ("standalone", "separate")):
                return target_plugin.display_name
        return "Juniper"

    @property
    def is_core(self):
        return self.category.lower() == "core"
