import juniper.engine.paths
import juniper.engine.types.script
import juniper.runtime.types.framework.singleton
import juniper.utilities.string as string_utils

import functools
import glob
import importlib
import json
import os


class PluginManager(object, metaclass=juniper.runtime.types.framework.singleton.Singleton):
    def __init__(self):
        self.plugin_cache = []

        # TODO! This plugin loading logic should all be handled in JuniperEngine, can it be removed?
        # Initialize all avaliable plugins
        '''plugins_root = os.path.join(juniper.engine.paths.root(), "Plugins")
        for plugin_group in os.listdir(plugins_root):
            plugin_group_dir = os.path.join(plugins_root, plugin_group)
            if(os.path.isdir(plugin_group_dir)):
                for plugin_name in os.listdir(plugin_group_dir):
                    plugin_dir = os.path.join(plugin_group_dir, plugin_name)
                    if(os.path.isdir(plugin_dir)):
                        for i in os.listdir(plugin_dir):
                            if(i.endswith(".jplugin")):
                                jplugin_path = os.path.join(plugin_dir, i)
                                self.plugin_cache.append(Plugin(jplugin_path))

        # Sort all avaliable plugins to ensure order of execution is adhered to:
        # 1) Juniper host plugins should always be first - as these have the most control over the workspace
        # 2) Juniper plugins should always come after host plugins so any worksplace additions are initialized
        # 3) All other plugins should come last
        juniper_plugins = []
        other_plugins = []

        for i in self.plugin_cache:
            if("\\juniper\\" in i.root.lower()):
                juniper_plugins.append(i)
            else:
                other_plugins.append(i)

        self.plugin_cache = juniper_plugins + other_plugins'''

    def __iter__(self):
        """
        Override the iterator method for the PluginManager to iterate over all available plugins
        :yield <Plugin:plugin> The current plugin
        """
        for i in self.plugin_cache:
            yield i

    def find_plugin(self, plugin_name):
        """
        Finds a plugin by its name
        :param <str:plugin_name> The name of the plugin to find
        :return <Plugin:plugin> The plugin if found - else None
        """
        plugin_name = plugin_name.lower()
        for i in self.plugin_cache:
            if(i.name == plugin_name):
                return i
        return None

    def register(self, plugin):
        """
        Registers a plugin
        :param <Plugin:plugin> The plugin to register
        """
        if(plugin not in self.plugin_cache):
            self.plugin_cache.append(plugin)

        # reorder the list so Juniper plugins are always first
        juniper_plugins = []
        other_plugins = []

        for i in self.plugin_cache:
            if("\\juniper\\" in i.root.lower()):
                juniper_plugins.append(i)
            else:
                other_plugins.append(i)

        self.plugin_cache = juniper_plugins + other_plugins


class Plugin(object):
    def __init__(self, jplugin_path):
        self.jplugin_path = jplugin_path
        PluginManager().register(self)

    def __repr__(self):
        return f"Plugin(\"{self.jplugin_path}\")"

    def __bool__(self):
        # check if supported in current host
        if(not self.is_enabled_in_host()):
            return False
        return True

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
        """
        :return <str:root> The root directory of this plugin
        """
        return os.path.dirname(self.jplugin_path)

    @property
    @functools.lru_cache()
    def name(self):
        """
        :return <str:name> The name of this plugin
        """
        return os.path.basename(self.jplugin_path).split(".")[0]

    @property
    @functools.lru_cache()
    def display_name(self):
        """
        :return <str:name> The friendly name of this plugin
        """
        return string_utils.snake_to_name(self.name)

    @property
    @functools.lru_cache()
    def enabled(self):
        """
        :return <bool:enabled> True if this plugin is enabled - else False
        """
        # If this is a host plugin (Ie, max, designer), and we're not in the context
        # the plugin should be disabled
        if("\\juniperhosts\\" in self.root.lower()):
            if(self.name != juniper.program_context):
                return False
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
                return json_data["internal"] is True
        return False

    # ---------------------------------------------------------------------

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

    # ---------------------------------------------------------------------

    def get_file(self, subdir, relative_path, override=None, require_override=False):
        """
        Gets a file for the plugin - with optional overrides
        :param <str:subdir> The name of the base directory to search
        :param <str:relative_path> The relative path for the file
        :param [<str:override>] Optional override for the file (Ie, "some_file.designer.txt")
        :param [<bool:require_override>] Is the override required? Or may we fallback to the non-overriden version
        :return <str:output> The file if found - else None
        """
        file_root = os.path.join(self.root, subdir)

        if(override):
            filename, _, filetype = relative_path.rpartition(".")
            override_relative_path = f"{filename}.{override}.{filetype}"
            override_abs_path = os.path.join(file_root, override_relative_path)
            if(os.path.isfile(override_abs_path)):
                return override_abs_path
            elif(require_override):
                return None

        abs_path = os.path.join(file_root, relative_path)
        if(os.path.isfile(abs_path)):
            return abs_path
        return None

    # ---------------------------------------------------------------------

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

    # ---------------------------------------------------------------------

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