import os
import functools
import json

import juniper.paths
import juniper.utilities.string as string_utils
import juniper.utilities.json as json_utils
from juniper.utilities import script_execution


class Macro(object):
    """Contains data on given tools for easy calling / binding"""
    def __init__(self, filepath, module=None):
        self._filepath = filepath
        self.module = module or "juniper"

    def run(self):
        """Run the macro"""
        script_execution.run_file(self.filepath, module=self.module)

    # ------------------------------------------------------------------------

    def __get_metadata_key(self, key):
        """Retrieves a metadata key from this macro source file
        :param <str:key> The key to get
        :return <str:value> The found value
        """
        output = ""

        if(self.is_toolptr):
            with open(self._filepath, "r") as f:
                json_data = json.load(f)
                if(key.lower() in json_data):
                    output = json_data[key.lower()]
        else:
            with open(self.filepath, "r") as f:
                for line in f.readlines():
                    if(line.startswith(f":{key.lower()}")):
                        output = line.split(" ", 1)[1].rstrip()
        return output

    # ------------------------------------------------------------------------

    @property
    def filepath(self):
        """Get the absolute filepath to the macro
        :return <str:filepath> Absolute path to the file this macro references
        """
        output = self._filepath
        if(self.is_toolptr):
            toolptr_path = json_utils.get_property(self._filepath, "path", check_local=False)
            output = juniper.paths.get_path(toolptr_path, self.module)
        return output

    @property
    def module_root(self):
        """Root directory of the module from the name
        :return <str:module_root> Root directory of the module
        """
        if(self.module):
            return juniper.paths.get_module_root(self.module)
        return juniper.paths.root()

    # ------------------------------------------------------------------------

    @property
    @functools.lru_cache()
    def display_name(self):
        """The friendly name of the macro
        :return <str:name> The name of the macro
        """
        possible_name = self.__get_metadata_key("name")       
        if(not possible_name):
            if(self.is_toolptr):
                possible_name = os.path.basename(self._filepath).split(".")[0]
            elif(os.path.basename(self.filepath) == "__init__.py"):
                possible_name = os.path.basename(os.path.dirname(self._filepath))
            else:
                possible_name = os.path.basename(self.filepath).split(".")[0]
            possible_name = string_utils.snake_to_name(possible_name)
        return possible_name

    @property
    @functools.lru_cache()
    def name(self):
        """The code name of the macro - this is just a lower case version of the name with no spaces or underscores
        :return <str:name>
        """
        return string_utils.friendly_to_code(self.display_name)

    @property
    @functools.lru_cache()
    def tooltip(self):
        """Gets the tooltip for this macro
        :return <str:tooltip> The tooltip for this macro
        """
        output = (
            self.__get_metadata_key("tooltip") or
            self.__get_metadata_key("summary") or
            self.display_name
        )
        return output

    # ------------------------------------------------------------------------

    @property
    @functools.lru_cache()
    def icon_path(self):
        """Gets the path to the icon metadata key
        :return <str:icon_path> Absolute path to the icon if set, else None
        """
        possible_path = self.__get_metadata_key("icon")
        if(possible_path):
            # TODO! Need a way to get relative paths for tools / plugins
            possible_path = juniper.paths.get_resource(possible_path.replace("\\\\", "\\"))
        return possible_path

    @property
    @functools.lru_cache()
    def has_icon(self):
        """Returns whether this macro uses an icon - if the icon is set but not found it is considered as not having one
        :return <bool:has_icon> True if there is a valid icon - else False
        """
        return os.path.isfile(self.icon_path)

    def get_icon(self):
        """Gets the QIcon for this macro if set
        :return <QIcon:icon> The icon for the macro if set - else None
        """
        from qtpy import QtGui
        if(self.has_icon):
            return QtGui.QIcon(self.icon_path)
        return None

    # ------------------------------------------------------------------------

    @property
    def module_name(self):
        """
        :return <str:name> The name of the juniper module this macro is a child of
        """
        module = self.get_module()
        if(not module):
            return "juniper"
        return module.name

    def get_module(self):
        """Searches for the module object this macro is a child of
        :return <Module:module> The module if found - else None
        """
        #import juniper.framework.backend.module
        #return juniper.framework.backend.module.ModuleManager.get_module(self.module)
        import juniper.framework.backend.plugin
        return juniper.framework.backend.plugin.PluginManager().find_plugin(self.module)


    @property
    @functools.lru_cache()
    def category(self):
        """Get the category structure for this macro
        :return <str:category> Category of the macro
        """
        possible_key = self.__get_metadata_key("category")
        if(possible_key):
            return possible_key.capitalize()
        return "Uncategorized"

    @property
    def is_toolptr(self):
        """Gets whether this macro is a toolptr
        :return <bool:is_toolptr> True if it's a toolptr - else False
        """
        return self._filepath.endswith(".toolptr")

    @property
    def sort_key(self):
        """
        :return <str:sort_key> Key used to sort this macro alphabetically
        """
        return self.category + "|" + self.display_name

    # ------------------------------------------------------------------------

    @property
    @functools.lru_cache()
    def parent_category(self):
        """
        Gets the outer most category for this tool, dependent on its parent module integration type
        (Ie, "Juniper" for integrated, or the module name for "Standalone" or "Separate")
        :return <str:category> The target category - defaults to "Juniper" if none is set
        """
        target_module = self.get_module()
        if(target_module and target_module.integration_type in ("standalone", "separate")):
            return target_module.display_name
        return "Juniper"

    @property
    @functools.lru_cache()
    def group(self):
        """
        Gets the group this tool is part of.
        Group is essentially a 1 layer deep version of category.
        :return <str:group> The name of the group
        """
        return self.__get_metadata_key("group") or ""

    # ------------------------------------------------------------------------

    @property
    def is_core_macro(self):
        """
        :return <bool:state> True if it is a core macro - else False
        """
        return self.category == "Core"


class __MacroManager(object):
    __instance__ = None

    def __init__(self):
        self.registered_macros = {}

    def check_if_file_is_macro(self, file):
        """
        :return <bool:is_macro> True if the file path is a valid macro - else False
        """
        if(file.endswith((".ms", ".py", ".toolptr"))):
            with open(file, "r") as f:
                if(file.endswith(".toolptr")):
                    json_data = json.load(f)
                    if("category" in json_data):
                        return True
                elif(file.endswith(".py") or (file.endswith(".ms") and juniper.program_context == "max")):
                    for line in f.readlines():
                        if(line.rstrip("\n") == ":type tool"):
                            return True
        return False

    def register_macro(self, macro):
        """Store a macro globally
        :param <Macro:macro> The macro to register
        """
        found_with_name = False

        if(macro.module in self.registered_macros):
            for i in self.registered_macros[macro.module]:
                if(self.registered_macros[macro.module][i].name == macro.name):
                    found_with_name = True

        if(not found_with_name):
            if(macro.module in self.registered_macros):
                self.registered_macros[macro.module][macro.name] = macro
            else:
                self.registered_macros[macro.module] = {macro.name: macro}

    @property
    def all_macros(self):
        """Gets all registered macros in a single list
        :return <[Macro]:macros> All macros
        """
        return list(self.registered_macros.values())

    def find_macro(self, macro_category, macro_name):
        """Searches for a macrom given an code name for the macro (no spaces or underscores)
        :param <str:macro_category> Category to search in
        :param <str:macro_name> Code name of the macro to search for
        :return <Macro:macro> The macro if found - else None
        """
        macro_category = macro_category.lower()
        macro_name = string_utils.friendly_to_code(macro_name)
        if(macro_category in self.registered_macros):
            if(macro_name in self.registered_macros[macro_category]):
                return self.registered_macros[macro_category][macro_name]
        return None

    def run_macro(self, macro_category, macro_name):
        """Run a macro from category+name
        :param <str:macro_category> Category of the macro
        :param <str:macro_name> Name of the macro
        """
        macro = self.find_macro(macro_category, macro_name)
        if(macro):
            macro.run()

    def __iter__(self):
        all_macros = []
        for module_name in self.registered_macros:
            for macro_name in self.registered_macros[module_name]:
                all_macros.append(self.registered_macros[module_name][macro_name])
        for i in sorted(all_macros, key=lambda x: x.sort_key):
            yield i


if(not __MacroManager.__instance__):
    __MacroManager.__instance__ = __MacroManager()
MacroManager = __MacroManager.__instance__
