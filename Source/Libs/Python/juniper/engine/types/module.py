import inspect
import glob
import os
import sys
from importlib.machinery import SourceFileLoader

import juniper.types.framework.singleton
import juniper.utilities.string


class ModuleManager(object, metaclass=juniper.types.framework.singleton.Singleton):
    def __init__(self):
        self.__registered_modules = []

    def get_module_class(self, module_path):
        """
        Returns a module class from the `__module__.py` file
        :param <str:module_path> The path to the target modules `__module__.py`
        """
        module_name = os.path.basename(os.path.dirname(module_path))
        module_name = juniper.utilities.string.friendly_to_code(module_name)
        module_import_name = f"juniper.modules.{module_name}"
        module = SourceFileLoader(module_import_name, module_path).load_module(module_import_name)
        for _, member_data in inspect.getmembers(module):
            if(inspect.isclass(member_data) and issubclass(member_data, Module)):
                return member_data
        return None

    def __iter__(self):
        """
        :yield <Module:module> Yielids all registered modules
        """
        for i in self.__registered_modules:
            yield i

    def register(self, module):
        """
        Registers a module
        :param <Module:module> The module to register
        """
        self.__registered_modules.append(module)


class Module(object):
    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        output = None
        root = cls.get_root()
        for i in ModuleManager():
            if(i.root == root):
                output = i
        if(not output):
            output = super(Module, cls).__new__(cls)
            output.__init__(*args, **kwargs)
            ModuleManager().register(output)
        return output

    def on_pre_startup(self):
        pass

    def on_startup(self):
        pass

    def on_post_startup(self):
        pass

    def on_shutdown(self):
        pass

    # ----------------------------------------------------------

    @classmethod
    def get_root(cls):
        """
        :return <str:root> The root directory for this module
        """
        return os.path.dirname(sys.modules[cls.__module__].__file__)

    @property
    def root(self):
        """
        :return <str:root> The root directory for this module
        """
        return self.get_root()

    @property
    def scripts(self):
        output = []
        for i in glob.iglob(self.root + "\\Source\\Scripts\\**\\*.*", recursive=True):
            script = juniper.engine.types.script.Script(i)
            if(script and script.get("type") == "script"):
                output.append(script)
        return output

    @property
    def tools(self):
        # NOTE: Do we want tools for modules? Should  modules just not have tools?
        output = []
        for i in glob.iglob(self.root + "\\Source\\Tools\\**\\*.*", recursive=True):
            script = juniper.engine.types.script.Script(i)
            if(script and script.get("type") == "tool"):
                output.append(script)
        return output
