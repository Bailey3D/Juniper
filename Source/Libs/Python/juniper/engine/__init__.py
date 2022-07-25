import functools
import glob
import importlib
import json
import os
import sys
from importlib.machinery import SourceFileLoader


class JuniperEngine(object):

    def __init__(self, bootstrap=False):
        """
        Base singleton class used for the Juniper engine.
        """
        if(bootstrap):
            if("juniper:install=true" in sys.argv):
                self.__install__()
            if("juniper:startup=true" in sys.argv):
                self.__bootstrap__()

    def __new__(cls, *args, **kwargs):
        """
        Override for __new__ to add support for TypeWrapperManager caching to avoid construction each gather
        """
        import juniper_globals
        if(not juniper_globals.get("juniper_engine")):
            output = super(JuniperEngine, cls).__new__(cls)
            juniper_globals.set("juniper_engine", output)
            kwargs["bootstrap"] = True
            output.__init__(*args, **kwargs)
        return juniper_globals.get("juniper_engine")

    def __install__(self):
        """
        Installs Juniper to the current machine by setting the current workspace path in appdata
        """
        sys.argv.remove("juniper:install=true")
        if(not os.path.isdir(self.appdata_dir)):
            os.makedirs(self.appdata_dir)

        data = {"path": self.workspace_root}

        with open(self.juniper_config_path, "w") as f:
            json.dump(data, f)

        self.on_install()

    def __uninstall__(self):
        """
        Uninstalls juniper from the current machine
        """
        # 1) Remove from appdata
        if(os.path.isfile(self.juniper_config_path)):
            os.remove(self.juniper_config_path)

    def __startup__(self):
        """
        run the startup process for Juniper in the current program context
        """
        sys.argv.remove("juniper:startup=true")
        # 1) Initialize core juniper libraries
        sys.path.insert(0, os.path.join(self.workspace_root, "Source\\Libs\\Python"))

        if(self.program_context != "python"):
            sys.path.append(os.path.join(self.workspace_root, "Source\\Hosts", self.program_context, "Source\\Libs\\Python"))

        sys.path.append(os.path.join(
            self.workspace_root,
            f"Cached\\PyCache\\Python{self.python_version_major}{self.python_version_minor}\\site-packages"
        ))

        # 2) Refresh imports
        # We must reload the base module here as when we're in standalone Python mode
        # the stub 'juniper.py' module is used as a hook to run startup files.
        # After the core juniper paths have been added to sys.path we will no longer need this
        # and should instead import the actual juniper module.
        import juniper
        importlib.reload(juniper)

        # 3) Initialize plugins
        for i in self.plugins:
            sys.path.append(os.path.join(i.root, "Source\\Libs\\Python"))

        # 4) Initialize globals
        import juniper_globals
        setattr(juniper, "program_context", self.program_context)
        juniper_globals.set("program_context", self.program_context)
        setattr(juniper, "log", self.log)
        juniper_globals.set("log", self.log)

        # 5) Run startup scripts for all plugins
        self.on_startup()
        self.broadcast("pre_startup")
        self.broadcast("startup")
        self.broadcast("post_startup")

    def __bootstrap__(self):
        """
        Run the bootstrap process for Juniper in the current program context
        """
        # 1) Check if the current program is enabled
        # ..

        # 2) Run bootstrap updates (pip packages)
        updater_source_path = os.path.join(self.workspace_root, "Source\\libs\\python\\juniper\\bootstrap\\updater.py")
        updater_module = SourceFileLoader("juniper.bootstrap.updater", updater_source_path).load_module()
        updater = updater_module.Updater(self)
        updater.run()

        # 3) Run startup
        self.__startup__()

    def __shutdown__(self):
        """
        Run the shutdown process for Juniper
        """
        import juniper_globals

        # Remove all Juniper arguments
        for i in reversed(sys.argv):
            if(i.startswith("juniper:")):
                sys.argv.remove(i)

        self.on_shutdown()
        juniper_globals.set("juniper_engine", None)

    # -------------------------------------------------------------------

    def shutdown(self):
        """
        Run the shutdown process for Juniper
        """
        self.__shutdown__()

    # -------------------------------------------------------------------

    def on_startup(self):
        """
        Overrideable startup method for host implementations
        """
        pass

    def on_install(self):
        """
        Overrideable install method for host implementations
        """
        pass

    def on_shutdown(self):
        """
        Overrideable shutdown method for host implementations
        """
        pass

    # -------------------------------------------------------------------

    def create_bootstrap_file(self, destination_path):
        """
        Creates a bootstrap path for the given program context - which is used to hook to Juniper startup in a given host application
        TODO! Support for overriding how the bootstrap is called (Ie, Blender and Painter require specific function boilerplate)
        :param <str:destination_path> The path to the bootstrap file
        """
        # 1) Boulerplate arguments (startup + context)
        file_lines = []
        file_lines.append("import sys\n")
        file_lines.append("sys.argv.append(\"juniper:startup=true\")\n")
        file_lines.append(f"sys.argv.append(\"juniper:program_context={self.program_context}\")\n")

        # 2) Add source lines in the bootstrap module
        bootstrap_source_lines = []
        bootstrap_module_path = os.path.join(self.workspace_root, "Source\\Libs\\Python\\juniper\\engine\\bootstrap.py")
        with open(bootstrap_module_path, "r") as f:
            bootstrap_source_lines = f.readlines()
        file_lines += bootstrap_source_lines

        # 3) Boilerplate code for calling bootstrap
        file_lines += [x + "\n" for x in self.bootstrap_call_lines()]
        #file_lines += "Bootstrap()"  # TODO!

        # 4) Create
        if(not os.path.isdir(os.path.dirname(destination_path))):
            os.makedirs(os.path.dirname(destination_path))
        with open(destination_path, "w") as f:
            f.writelines(file_lines)

    def bootstrap_call_lines(self):
        """
        Overrideable method used to implement different boilerplate methods of calling the Boilerplate / startup
        Programs such as Blender / Painter require specific boilerplate in order to run startup scripts
        :return <[str]:lines> The lines to add to the end of the boilerplate script
        """
        return ["Bootstrap()", ]

    # -------------------------------------------------------------------

    @property
    def scripts(self):
        """
        :return <[Script]:scripts> All available scripts in the current context
        """
        output = []

        # host implementation scripts
        import juniper.engine.types.script
        if(self.program_context != "python"):
            host_root = os.path.join(
                self.workspace_root,
                "Source\\Hosts",
                self.program_context,
                "Source\\Scripts"
            )
            for i in glob.iglob(host_root + "\\**\\*.*"):
                script = juniper.engine.types.script.Script(i)
                if(script):
                    output.append(script)

        # Note: No core scripts. The base Juniper workspace should not rely on scripts during startup.

        for plugin in self.plugins:
            for s in plugin.scripts:
                if(s.is_enabled_in_host(self.program_context)):
                    output.append(s)
        return output

    @property
    def tools(self):
        """
        :return <[Script]:tools> All available tools in the current context
        """
        output = []

        # Note: No core / host tools. The base implementations should be empty.

        for plugin in self.plugins:
            for s in plugin.tools:
                if(s.is_enabled_in_host(self.program_context)):
                    output.append(s)
        return output

    @property
    def plugins(self):
        """
        :return <[Plugin]:plugins> Returns all registered plugins
        """
        import juniper.bootstrap.types.plugin

        output = []
        for i in self.plugin_paths:
            plugin = juniper.bootstrap.types.plugin.Plugin(i)
            if(plugin):
                output.append(plugin)

        return output

    @property
    def plugin_paths(self):
        """
        :return <[str]:paths> The paths to all found .jplugin files
        """
        output = []
        for i in glob.glob(self.workspace_root + "\\Plugins\\**\\*.jplugin", recursive=True):
            output.append(i)
        return output

    def broadcast(self, callback_name):
        """
        Broadcasts a callback by its name
        :param <str:callback_name> The name of the callback to broadcast
        """
        target_scripts = []

        check_scripts = True
        check_tools = callback_name not in ("pre_startup", "startup", "post_startup")

        if(check_scripts):
            for i in self.scripts:
                if(i and i.is_bound_to_callback(callback_name)):
                    target_scripts.append(i)
        if(check_tools):
            for i in self.tools:
                if(i and i.is_bound_to_callback(callback_name)):
                    target_scripts.append(i)

        for i in target_scripts:
            print(f"Running: {i.path}")
            i.run()

    # -------------------------------------------------------------------

    def find_tool(self, tool_name):
        """
        Finds a tool by its name
        :param <str:name> The name of the tool
        :return <Script:tool> The tool if found - else None
        """
        for i in self.tools:
            if(i.file_name == tool_name):
                return i
        return None

    # -------------------------------------------------------------------

    @property
    def python_version(self):
        """
        Return the python version (Major.Minor ONLY)
        :return <float:version> Formatted MAJOR.MINOR (Ie, 3.7)
        """
        return float(f"{sys.version_info[0]}.{sys.version_info[1]}")

    @property
    def python_version_major(self):
        """
        :return <int:major> Returns the python major version (Ie, 3)
        """
        return int(str(self.python_version).split(".")[0])

    @property
    def python_version_minor(self):
        """
        :return <int:minor> Returns the python minor version (Ie, 10)
        """
        return int(str(self.python_version).split(".")[1])

    @property
    def python_path(self):
        """
        Gets the path to the current host Python exe
        We cannot rely on `sys.executable` as it will return the host application exe when using embedded Python (Ie, unreal.exe)
        Note: Override this for host applications which use a non-standard Python folder structure (Ie, Blender)
        :return <str:path> The path to the exe if found - else None
        """
        output = None

        check_dir = os.path.dirname(os.__file__)
        while(not output and len(check_dir) > 3):
            possible_exe_path = os.path.join(check_dir, "python.exe")
            if(os.path.isfile(possible_exe_path)):
                output = possible_exe_path
            else:
                check_dir = os.path.dirname(check_dir)

        return output

    # -------------------------------------------------------------------

    @staticmethod
    @functools.lru_cache()
    def get_workspace_root():
        """
        :return <str:dir> The root directory for the Juniper workspace
        """
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\..\\..\\..\\.."))

    @property
    @functools.lru_cache()
    def workspace_root(self):
        """
        :return <str:dir> The root directory for the Juniper workspace
        """
        return self.get_workspace_root()

    @property
    def appdata_dir(self):
        """
        :return <str:dir> The root directory for Juniper data in "AppData/Roaming"
        """
        return os.path.join(os.getenv("APPDATA"), "Juniper")

    @property
    @functools.lru_cache()
    def juniper_config_path(self):
        """
        :return <str:path> The path to the base juniper config json file
        """
        return os.path.join(
            self.appdata_dir,
            "config.json"
        )

    # -------------------------------------------------------------------

    @staticmethod
    def get_program_context():
        """
        :return <str:context> The name of the current host application from the engine override class name
        """
        for i in sys.argv:
            if(i.startswith("juniper:program_context=")):
                return i.split("=")[1].lower()
        return "python"

    @property
    @functools.lru_cache()
    def program_context(self):
        """
        :return <str:context> The name of the current host application from the engine override class name
        """
        return self.get_program_context()

    @property
    @functools.lru_cache()
    def log(self):
        import juniper.logging
        return juniper.logging.Log(plugin="Juniper")

    @staticmethod
    @functools.lru_cache()
    def get_supported_hosts():
        """
        :return <[str]:hosts> The names of all supported hosts (in the "Plugins\\JuniperHosts\\" directory)
        """
        output = []
        hosts_dir = os.path.join(JuniperEngine.get_workspace_root(), "Source\\Hosts")
        for i in os.listdir(hosts_dir):
            host_dir = os.path.join(hosts_dir, i)
            if(os.path.isdir(host_dir)):
                output.append(i.lower())
        return output

    @property
    def supported_hosts(self):
        """
        :return <[str]:hosts> The names of all supported hosts (in the "Plugins\\JuniperHosts\\" directory)
        """
        return self.get_supported_hosts()

    # -------------------------------------------------------------------

    @property
    def site_packages_dir(self):
        """
        :return <str:dir> The directory of the external site packages - respective of the current Python major/minor version
        """
        return os.path.join(
            self.workspace_root,
            f"Cached\\PyCache\\Python{self.python_version_major}{self.python_version_minor}\\site-packages"
        )

    def core_library_paths(self):
        """
        :return <[str]:dirs> The directories to all core/required python libraries
        """
        output = []
        output.append(os.path.join(self.workspace_root, "Source\\Libs\\python"))
        output.append(self.site_packages_dir)
        return output
