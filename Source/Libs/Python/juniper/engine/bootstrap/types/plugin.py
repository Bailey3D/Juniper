import functools
import glob
import importlib
import json
import os

import juniper
import juniper.engine.types.script


class Plugin(object):
    def __init__(self, jplugin_path):
        """
        Barebones class for a plugin - used during the bootstrap phase
        This is overriden in `juniper.engine.types.plugin` for a version including more features
        """
        self.jplugin_path = jplugin_path

    def __bool__(self):
        # check if supported in the current host
        if(not self.is_enabled_in_host()):
            return False

        return True

    # ------------------------------------------------------------------------------

    def on_tick(self):
        """
        Overrideable method called each tick
        """
        pass

    def on_pre_startup(self):
        """
        Overrideable method called before startup
        """
        pass

    def on_startup(self):
        """
        Overrideable method called during startup
        """
        pass

    def on_post_startup(self):
        """
        Overrideable method called after startup
        """
        pass

    # ------------------------------------------------------------------------------

    def get(self, key):
        """
        Gets a key from the file metadata of this script
        :param <str:key> The key to get
        :return <str:value> The value as stored in the script
        """
        key = key.lower()
        if(key in self.metadata):
            return self.metadata[key]
        return None

    @property
    @functools.lru_cache()
    def metadata(self):
        """
        :return <dict:data> The jplugin file data loaded as a json dict
        """
        with open(self.jplugin_path, "r") as f:
            return json.load(f)

    # ------------------------------------------------------------------------------

    @property
    @functools.lru_cache()
    def name(self):
        """
        :return <str:name> The code name of this plugin
        """
        return os.path.basename(self.jplugin_path).split(".")[0]

    @property
    def root(self):
        return os.path.dirname(self.jplugin_path)

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
        output = []
        for i in glob.iglob(self.root + "\\Source\\Tools\\**\\*.*", recursive=True):
            script = juniper.engine.types.script.Script(i)
            if(script and script.get("type") == "tool"):
                output.append(script)
        return output

    @property
    def modules(self):
        import juniper.engine.types.module
        output = []
        module_paths = [x for x in glob.glob(self.root + "\\Source\\Modules\\**\\__module__.py", recursive=True)]
        for module_path in module_paths:
            module_class = juniper.engine.types.module.ModuleManager().get_module_class(module_path)
            if(module_class is not None):
                module_instance = module_class()
                output.append(module_instance)
        return output

    @property
    def python_module(self):
        try:
            output = importlib.import_module(self.name)
            return output
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------------------

    def is_enabled_in_host(self, target_host=None):
        """
        Checks if this script is enabled in the current host
        This checks against the `supported_hosts` and `unsupported_hosts` metadata keys
        If neither are provided, we return True
        :param <str:target_host> The name of the host to check
        :return <bool:enabled> True if enabled - else False
        """
        if(not target_host):
            target_host = juniper.program_context or "python"
        target_host = target_host.lower()
        supported_hosts = []
        unsupported_hosts = []

        if(self.get("supported_hosts")):
            for i in self.get("supported_hosts"):
                supported_hosts.append(i.lower())

        if(self.get("unsupported_hosts")):
            for i in self.get("unsupported_hosts"):
                unsupported_hosts.append(i.lower())

        if(target_host not in unsupported_hosts):
            if(not supported_hosts or target_host in supported_hosts):
                return True

        return False
