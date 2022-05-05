import juniper.paths
import juniper.framework.metadata
import juniper.framework.types.singleton
from juniper.framework.tooling import macro
import juniper.utilities.string as string_utils

import functools
import glob
import json
import os
import sys


class PluginManager(object, metaclass=juniper.framework.types.singleton.Singleton):
    def __init__(self):
        self.plugin_cache = []

        plugins_root = os.path.join(juniper.paths.root(), "Plugins")
        for i in os.listdir(plugins_root):
            plugin_dir = os.path.join(plugins_root, i)
            for i in os.listdir(plugin_dir):
                if(i.endswith(".jplugin")):
                    jplugin_path = os.path.join(plugin_dir, i)
                    self.plugin_cache.append(Plugin(jplugin_path))

    def __iter__(self):
        for i in self.plugin_cache:
            yield i

    def find_plugin(self, plugin_name):
        for i in self.plugin_cache:
            if(i.name == plugin_name):
                return i
        return None


class Plugin(object):
    def __init__(self, jplugin_path):
        self.jplugin_path = jplugin_path

    @property
    @functools.lru_cache()
    def plugin_metadata(self):
        """
        :return <dict:metadata> The jplugin loaded as a dict
        """
        with open(self.jplugin_path, "r") as f:
            return json.load(f)

    @property
    @functools.lru_cache()
    def root(self):
        return os.path.dirname(self.jplugin_path)

    @property
    @functools.lru_cache()
    def name(self):
        return os.path.basename(self.jplugin_path).split(".")[0]

    @property
    @functools.lru_cache()
    def display_name(self):
        """
        :return <str:name> The friendly name of this module
        """
        return string_utils.snake_to_name(self.name)

    @property
    @functools.lru_cache()
    def enabled(self):
        if("enabled" in self.plugin_metadata):
            return self.plugin_metadata["enabled"]
        return True

    @property
    @functools.lru_cache()
    def internal(self):
        """
        :return <bool:internal> True if this is an internal (Juniper) plugin - else False
        """
        with open(self.jplugin_path, "r") as f:
            json_data = json.load(f)
            if("internal" in json_data):
                return json_data["internal"] == True
        return False
        

    # ---------------------------------------------------------------------

    @property
    def integration_type(self):
        """
        Gets the mode for how tools from this module are shown
        Options include:
        - integrated, for build into the top level juniper menu
        - standalone, for a separate menu all together
        - separate, for a submenu with the modules name
        :return <str:integration_type> The mode of the menu
        """
        if(self.name == "juniper"):
            return "integrated"
        if(os.path.isfile(self.jplugin_path)):
            with open(self.jplugin_path, "r") as f:
                json_data = json.load(f)
            if("integration_type" in json_data):
                value = json_data["integration_type"].lower()
                if(value in ("integrated", "standalone")):
                    return value
        return "separate"

    # ---------------------------------------------------------------------

    def __get_scripts(self, script_type, index=None):
        output = []

        if(index is None):
            # If None then just get the base '__startup__.py' file
            base_startup_script = os.path.join(self.root, f"Source\\{script_type}\\__startup__.py")
            if(os.path.isfile(base_startup_script)):
                output.append(base_startup_script)
        else:
            # Else we want all scripts in the target tier folder
            # TODO! We need a way to get the programs a script is enabled in
            # Ie, :supported_programs [max, ue4]
            startup_scripts_dir = os.path.join(self.root, f"Source\\{script_type}\\{index}")
            if(os.path.isdir(startup_scripts_dir)):
                for i in glob.glob(startup_scripts_dir + "\\**\\*.*", recursive=True):
                    if(i.endswith(".py")):
                        output.append(i)
                    elif(i.endswith(".ms") and juniper.program_context == "max"):
                        output.append(i)
        return output

    def startup_scripts(self, index=None):
        return self.__get_scripts("Startup", index=index)

    def install_scripts(self, index=None):
        return self.__get_scripts("Install", index=index)

    # ---------------------------------------------------------------------

    def initialize_macros(self):
        """
        Initializes all macros in this module
        :return <[Macro]:macros> All macros registered for this module
        """
        output = []
        macro_file_paths = []

        tools_root_dir = os.path.join(self.root, "Source\\Tools")
        for file in glob.iglob(tools_root_dir + "\\**", recursive=True):
            if(file.endswith((".ms", ".py", ".toolptr"))):
                if(file not in macro_file_paths):
                    with open(file, "r") as f:
                        if(file.endswith(".toolptr")):
                            json_data = json.load(f)
                            if("category" in json_data):
                                macro_file_paths.append(file)
                        elif(file.endswith(".py") or (file.endswith(".ms") and juniper.program_context == "max")):
                            if(file not in macro_file_paths):
                                file_metadata = juniper.framework.metadata.FileMetadata(file)
                                if(file_metadata.get("type") == "tool"):
                                    print(":)")
                                    macro_file_paths.append(file)
                                    break

        for file in macro_file_paths:
            m = macro.Macro(file, module=self.name)
            m.module = self.name
            macro.MacroManager.register_macro(m)
            output.append(m)

        return output


    @property
    def core_macros(self):
        # TODO!
        pass

    @property
    def macros(self):
        # TODO!
        output = []
        for i in macro.MacroManager:
            if(i.module_name == self.name and not i.is_core_macro):
                output.append(i)
        return output

    def initialize_libraries(self):
        sys.path.append(os.path.join(self.root, "Source\\Libs\\Python"))
