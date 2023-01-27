import importlib
import inspect
import os
import sys
from importlib.machinery import SourceFileLoader

import juniper
import juniper.engine.paths


class JuniperImportHook(object):
    def __init__(self):
        """
        Class added to `sys.meta_path` to hook post-import logic for juniper libraries
        """
        sys.meta_path.insert(0, self)
        self.checked_modules = set()

    @property
    def current_host(self):
        """
        :return <str:name> The name of the current host context
        """
        return juniper.program_context

    @property
    def current_host_root(self):
        """
        :return <str:dir> The root directory of the current host implementation
        """
        if(self.current_host):
            return os.path.join(juniper.engine.paths.root(), "Source\\Hosts", self.current_host)
        return None

    def find_module(self, full_name, path=None):
        """
        Delegate called to find a module given its name
        :param <str:full_name> The name of the module to find
        :param [<str:path>] The path to the file
        """
        # TODO! Juniper Engine: Only run this for Juniper library modules
        if(not full_name.startswith("juniper")):
            return None

        if(full_name in self.checked_modules):
            return None

        self.checked_modules.add(full_name)
        return self

    def post_import(self, module, module_name):
        """
        Ran after a successful import of a Juniper based module
        This function will search for overrides - given the current host context
        and implement them to the module for this and future imports
        :param <Module:module> The imported module
        :param <str:module_name> The name of the module
        """
        module_overrides = self.find_file_overrides(module.__file__, check_core=False)
        if(not module_overrides):
            return None

        override_module_name = f"{module_name}.override"
        override_loader = SourceFileLoader(override_module_name, module_overrides[0])
        override_module = override_loader.load_module(override_module_name)

        # this will override the module saved to sys.modules
        # meaning all imports from now on will get this one
        # the override module however will keep its reference to the parent module
        # Note: This probably won't work if we run `importlib.reload` on the module after this point!
        sys.modules[module_name] = override_module

        # add all attributes which are missing from the original module to this new one
        for k, v in inspect.getmembers(module):
            if(not hasattr(override_module, k)):
                setattr(override_module, k, v)

        # TODO! Juniper Engine: For `__init__.py` files the path will be updated to the override directory
        # this should keep the original path
        # ..

    def load_module(self, full_name):
        """
        Core logic for loading a module
        :param <str:full_name> The name of the module
        """
        importlib.import_module(full_name)
        module = sys.modules[full_name]
        self.checked_modules.remove(full_name)
        self.post_import(module, full_name)
        return module

    # ---------------------------------------------------------------------------

    def find_file_overrides(self, file_path, check_core=True, check_host=True):
        """
        Gets the path to an overriden version of this file (Ie, "vector.py" -> "vector.designer.py" when overriden)
        :param <str:file_path> The path to the base file
        :return <str:override> The override file path if we have a host open - else None
        """
        output = []

        # check for a file override (Ie, "vector.designer.py")
        if(check_core):
            file_name = os.path.basename(file_path)
            file_name_split = file_name.rsplit(".", 1)  # 0 = file name, 1 = file type
            override_file_name = f"{file_name_split[0]}.{self.current_host}.{file_name_split[1]}"
            file_with_override = os.path.join(os.path.dirname(file_path), override_file_name)

            if(file_with_override != file_path and os.path.isfile(file_with_override)):
                output.append(file_with_override)

        # check for host override
        if(check_host):
            file_with_override_in_host = file_path.replace(
                juniper.engine.paths.root(),
                f"{juniper.engine.paths.root()}\\Source\\Hosts\\{self.current_host}"
            )

            if(file_with_override_in_host != file_path and os.path.isfile(file_with_override_in_host)):
                output.append(file_with_override_in_host)

        return output
