"""
Base class for Juniper modules
"""
from collections import OrderedDict
import functools
import glob
import json
import os
import sys

import juniper.framework.backend.program
import juniper.utilities.script_execution
import juniper.framework.tooling.macro
import juniper.framework.versioning
import juniper.framework.vscode
import juniper.paths
import juniper.utilities.json as json_utils
import juniper.utilities.string as string_utils
from juniper.framework.tooling import macro


class __ModuleManager(object):
    __instance__ = None

    def __init__(self):
        self.module_cache = OrderedDict()

    def register_module(self, module):
        self.module_cache[module.name] = module

    def get_module(self, module_name):
        module_name = module_name.lower()
        if(module_name in self.module_cache):
            return self.module_cache[module_name]
        self.register_module(Module(module_name))

    def program_names(self):
        """
        Get a list of all juniper program names
        :return <[str]:names> List of all program names
        """
        output = []
        scripts_dir = os.path.join(juniper.paths.root(), "scripts")
        for i in os.listdir(scripts_dir):
            install_dir = os.path.join(scripts_dir, i, "install")
            if(i != "common" and os.path.isdir(install_dir)):
                output.append(i.lower())
        return output

    def is_program_enabled(self, program_name):
        """
        Returns whether a program is enabled
        :param <str:program_name> The name of the program to check
        :return <bool:enabled> True if the program is enabled - else False
        """
        program_name = program_name.lower()
        if(program_name in ("python", "common")):
            return True
        elif(program_name not in self.program_names()):
            return False
        client_settings_path = juniper.paths.get_config("client_settings.json")
        if(os.path.isfile(client_settings_path)):
            enabled = json_utils.get_property(client_settings_path, "programs" + "." + program_name + ".enabled")
            return not (enabled is False)
        return True

    def __iter__(self):
        for i in self.module_cache:
            yield self.module_cache[i]

    def find(self, module_name):
        if(module_name in self.module_cache):
            return self.module_cache[module_name]
        return None


if(not __ModuleManager.__instance__):
    __ModuleManager.__instance__ = __ModuleManager()
ModuleManager = __ModuleManager.__instance__


# --------------------------------------------------------------------------------------

class Module(object):
    """Base class for Juniper modules"""
    def __init__(self, module_name, module_dir=None):
        self.__module_name = module_name
        self.__module_dir = module_dir
        ModuleManager.register_module(self)

    @property
    @functools.lru_cache()
    def module_root(self):
        if(self.__module_name == "juniper"):
            return juniper.paths.root()
        return self.__module_dir or juniper.paths.get_module_root(self.__module_name)

    @property
    @functools.lru_cache()
    def name(self):
        """
        :return <str:module_name> Name of the module
        """
        if(self.__module_name == "juniper"):
            return "juniper"
        for i in os.listdir(self.module_root):
            if(i.endswith(".jmodule")):
                return i.split(".")[0].lower()
                #return i.rstrip(".jmodule").lower()
        return self.__module_name.lower()

    @property
    def display_name(self):
        """
        :return <str:name> The friendly name of this module
        """
        return string_utils.snake_to_name(self.name)

    @property
    @functools.lru_cache()
    def enabled(self):
        """
        :return <bool:is_enable> True if enabled - else False
        """
        client_settings_path = juniper.paths.get_config("client_settings.json.local")
        if(os.path.isfile(client_settings_path)):
            if(self.name not in ("python", "juniper")):
                enabled = json_utils.get_property(client_settings_path, f"modules.{self.name}.enabled")
                return not (enabled is False)
        return True

    # --------------------------------------------------------------------------------------

    @property
    def integration_type(self):
        """Gets the mode for how tools from this module are shown
        Options include:
        - integrated, for build into the top level juniper menu
        - standalone, for a separate menu all together
        - separate, for a submenu with the modules name
        :return <str:integration_type> The mode of the menu
        """
        jmodule_file = os.path.join(self.module_root, self.name + ".jmodule")
        if(self.name == "juniper"):
            return "integrated"
        if(os.path.isfile(jmodule_file)):
            with open(jmodule_file, "r") as f:
                json_data = json.load(f)
            if("integration_type" in json_data):
                value = json_data["integration_type"].lower()
                if(value in ("integrated", "standalone")):
                    return value
        return "separate"

    # --------------------------------------------------------------------------------------

    def get_resource_directory(self, directory_name, program="common"):
        """
        Gets a resource directory for a module
        :param <str:directory_name> Name of the directory to get
        :param [<str:program>] The name of the program to target - defaults to "common"
        :return <str:dir> The target directory
        """
        return os.path.join(self.module_root, directory_name, program)

    @property
    @functools.lru_cache()
    def common_startup_dir(self):
        """
        :return <str:dir> The scripts directory for common
        """
        return os.path.join(
            juniper.paths.root(),
            "scripts\\common\\startup"
        )

    # --------------------------------------------------------------------------------------

    @property
    def python_lib_dir(self):
        """
        :return <str:dir> The base directory for the module python library
        """
        return os.path.join(self.module_root, "lib\\python")

    @property
    def python_lib_external_dir(self):
        """
        :return <str:dir> The directory for the external python libraries
        """
        return os.path.join(
            self.module_root,
            "lib\\external",
            f"python{str(juniper.framework.versioning.python_version())}",
            "site-packages"
        )

    @property
    def python_lib_programs_dir(self):
        """
        :return <str:dir> The directory to the programs sub-package
        """
        return os.path.join(self.python_lib_dir, self.name, "programs")

    def initialize_libraries(self):
        """Initializes the sys paths for the module libraries"""
        if(self.enabled):
            sys.path.append(self.python_lib_dir)
            sys.path.append(self.python_lib_external_dir)
            try:
                exec(f"import {self.name}")
                module = juniper.utilities.script_execution.load_source(
                    self.name,
                    os.path.join(self.module_root, "lib\\python", self.name, "__init__.py")
                )
                module.__path__.append(self.python_lib_programs_dir)
                module.__path__.append(self.tools_common_dir)
                module.__path__.append(self.tools_program_dir)
                module.__path__.append(self.tools_common_dir)
                module.__path__.append(self.tools_program_dir)
                for program_name in ModuleManager.program_names():
                    module.__path__.append(os.path.join(self.python_lib_programs_dir, program_name))
            except ModuleNotFoundError:
                # Exception should pass quietly if this module does not implement a base python library
                pass
            except Exception as e:
                print(type(e))
                juniper.log.error(str(e))

    # --------------------------------------------------------------------------------------

    @property
    def tools_common_dir(self):
        """
        :return <str:dir> The directory containing the common tools for this module
        """
        return os.path.join(self.module_root, "scripts\\common")

    @property
    def tools_program_dir(self):
        """
        :return <str:dir> The directory containing the common tools for this module
        """
        return os.path.join(self.module_root, "scripts", juniper.framework.backend.program.program_context())

    # --------------------------------------------------------------------------------------

    @property
    def scripts_common_dir(self):
        """
        :return <str:dir> The directory to the common scripts
        """
        return os.path.join(self.module_root, "scripts\\common")

    @property
    def scripts_program_dir(self):
        """
        :return <str:dir> The directory to the current program scripts
        """
        return os.path.join(self.module_root, "scripts", juniper.framework.backend.program.program_context())

    @property
    def startup_scripts_common_dir(self):
        """
        :return <str:dir> The directory to the common startup scripts
        """
        return os.path.join(self.module_root, "scripts\\common\\startup")

    @property
    def startup_scripts_program_dir(self):
        """
        :return <str:dir> The directory to the common startup scripts
        """
        return os.path.join(self.module_root, "scripts", juniper.framework.backend.program.program_context(), "startup")

    def get_startup_scripts(self, startup_index):
        """
        Gets the paths to all startup scripts for this module at the given index
        :param <int:startup_index> The startup index to get scripts for
        :return <[str]:paths> The paths to all target scripts
        """
        output = set()

        if(startup_index is None):
            # If startup index is None then we're after the base `__startup__.py` scripts
            for i in (
                self.scripts_common_dir,
                self.scripts_program_dir,
                #self.startup_scripts_common_dir,
                #self.startup_scripts_program_dir
            ):
                possible_script_path = os.path.join(i, "__startup__.py")
                if(os.path.isfile(possible_script_path)):
                    output.add(possible_script_path)

        else:
            # Else we're just after a specific index
            for startup_dir in (
                self.startup_scripts_common_dir,
                self.startup_scripts_program_dir
            ):
                indexed_startup_dir = os.path.join(startup_dir, str(startup_index))
                for file in glob.glob(indexed_startup_dir + "\\*.py", recursive=True):
                    output.add(file)
                for file in glob.glob(indexed_startup_dir + "\\*.ms", recursive=True):
                    output.add(file)

                # maxscript hook
                if(juniper.framework.backend.program.program_context() == "max"):
                    dir_as_maxscript = indexed_startup_dir.replace("\\python", "\\maxscript")
                    for file in glob.glob(dir_as_maxscript + "\\*.ms", recursive=True):
                        output.add(file)

        return tuple(output)

    def run_startup_scripts(self, startup_index):
        """
        Runs a startup script from its index
        :param <int:startup_index> The index to run all scripts for - if None then the base `__startup__.py` script is ran.
        """
        for script in self.get_startup_scripts(startup_index):
            juniper.utilities.script_execution.run_file(script)
            juniper.log.info("Ran Startup Script: " + script, silent=True)

    # --------------------------------------------------------------------------------------

    def register_macros(self):
        """
        Registers all macros for this module
        """
        output = set()
        files = set()
        root_dirs = (
            self.tools_common_dir,
            self.tools_program_dir
        )

        for root_dir in root_dirs:
            for file in glob.glob(root_dir + "\\**", recursive=True):
                if(file.endswith((".ms", ".py", ".toolptr"))):
                    with open(file, "r") as f:
                        if(file.endswith(".toolptr")):
                            json_data = json.load(f)
                            if("category" in json_data and file not in files):
                                files.add(file)
                        else:
                            for line in f.readlines():
                                if(line.startswith(":tool") and file not in files):
                                    files.add(file)

        for i in files:
            _macro = macro.Macro(i, module=self.name)
            _macro.module = self.name
            macro.MacroManager.register_macro(_macro)
            output.add(_macro)

        return list(output)

    def get_macros(self):
        output = []
        for i in macro.MacroManager:
            if(i.module_name == self.name):
                if(not i.is_core_macro):
                    output.append(i)
        return output

    def get_core_macros(self):
        output = []
        for i in macro.MacroManager:
            if(i.module_name == self.name and i.is_core_macro):
                output.append(i)
        return output

    @property
    def macros(self):
        """
        Get instances of all macros for this module
        :return <[Macro]:macros> All macros for the current program
        """
        output = set()
        files = set()
        root_dirs = (
            self.tools_common_dir,
            self.tools_program_dir
        )

        for root_dir in root_dirs:
            for file in glob.glob(root_dir + "\\**", recursive=True):
                if(file.endswith((".ms", ".py", ".toolptr"))):
                    with open(file, "r") as f:
                        if(file.endswith(".toolptr")):
                            json_data = json.load(f)
                            if("category" in json_data and file not in files):
                                files.add(file)
                        else:
                            for line in f.readlines():
                                if(line.startswith(":tool") and file not in files):
                                    files.add(file)

        for i in files:
            _macro = macro.Macro(i, module=self.name)
            _macro.module = self.name
            macro.MacroManager.register_macro(_macro)
            output.add(_macro)

        return list(output)


class ModuleCreator(object):
    def __init__(self, module_name, module_display_name, integration_type="standalone"):
        """
        Helper class used to create a Juniper Module
        :param <str:module_name> The code name of the module (Ie, "tools_library")
        :param <str:module_display_name> The display name of the module (Ie, "Tools Library")
        :param [<str:integration_type>] How are tools from this module integrated into Juniper?
        """
        self.module_name = module_name
        self.module_display_name = module_display_name
        self.integration_type = integration_type

    @property
    def integration_types(self):
        """
        :return <[str]:integration_types> All vaild integration types
        """
        return (
            "Integrated",
            "Standalone",
            "Separate"
        )

    @property
    def jmodule_root(self):
        """
        :return <str:root> The root directory of this module
        """
        return os.path.join(juniper.paths.root(), "modules", self.module_display_name)

    @property
    def jmodule_path(self):
        """
        :return <str:path> The path to the module.jmodule file
        """
        return os.path.join(self.jmodule_root, self.module_name + ".jmodule")

    @property
    def jmodule_data(self):
        """
        :return <dict:data> The data that should be contained in the .jmodule file
        """
        return {
            "integration_type": self.integration_type
        }

    def create(self):
        """
        Creates all stub files for this juniper module
        """
        if(self.module_name):
            output_root = self.jmodule_root
            jmodule_path = self.jmodule_path

            paths = [
                f"{output_root}\\bin\\common\\.empty",
                f"{output_root}\\config\\common\\.empty",
                f"{output_root}\\lib\\python\\{self.module_name}\\__init__.py",
                f"{output_root}\\resources\\common\\.empty",
                f"{output_root}\\scripts\\common\\.empty",
                f"{output_root}\\shelves\\.empty"
            ]

            for i in paths:
                if(not os.path.isfile(i)):
                    os.makedirs(os.path.dirname(i))
                    with open(i, "w") as f:
                        f.write("")

            if(not os.path.isfile(jmodule_path)):
                with open(jmodule_path, "w") as f:
                    json.dump(self.jmodule_data, f, sort_keys=True)

            juniper.framework.vscode.update_code_workspace()
