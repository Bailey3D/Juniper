import functools
import glob
import importlib
import json
import os
import sys
from datetime import datetime
from importlib.machinery import SourceFileLoader


class JuniperEngine(object):

    def __init__(self, bootstrap=False):
        """
        Base singleton class used for the Juniper engine.
        """
        # tick
        self.delta_seconds = 0
        self.time_cf = datetime.now()

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

        # 3a) Initialize modules
        # module libraries should be within a stub `juniper` directory
        # as they are considered an extension of juniper - not standalone.
        import juniper.engine.types.module
        modules = []
        module_paths = [x for x in glob.glob(self.workspace_root + "\\Source\\Modules\\**\\__module__.py", recursive=True)]
        for module_path in module_paths:
            module_class = juniper.engine.types.module.ModuleManager().get_module_class(module_path)
            if(module_class is not None):
                module_instance = module_class()
                modules.append(module_instance)
                juniper.__path__.append(os.path.join(module_instance.root, "Source\\Libs\\Python\\juniper"))

        # 3b) Initialize plugins / plugin modules
        for i in self.plugins:
            sys.path.append(os.path.join(i.root, "Source\\Libs\\Python"))
            python_module = i.python_module
            for module in i.modules:
                if(python_module):
                    python_module.__path__.append(os.path.join(module.root, "Source\\Libs\\Python", i.name))

        # 4) Initialize globals
        import juniper_globals
        setattr(juniper, "program_context", self.program_context)
        juniper_globals.set("program_context", self.program_context)
        setattr(juniper, "log", self.log)
        juniper_globals.set("log", self.log)

        # Run pre-startup
        self.on_pre_startup()
        for i in self.plugins:
            pass  # TODO! Broadcast pre-startup to plugins
        for i in self.modules:
            i.on_pre_startup()

        # Run startup
        self.on_startup()
        for i in self.plugins:
            pass  # TODO! Broadcast startup to plugins
        for i in self.modules:
            i.on_startup()
        self.broadcast("pre_startup")

        # Run post-startup
        self.on_post_startup()
        for i in self.plugins:
            pass  # TODO! Broadcast post-startup to plugins
        for i in self.modules:
            i.on_post_startup()
        self.broadcast("startup")

        # 5) Run startup scripts for all plugins
        self.on_startup()
        for i in self.plugins:
            pass
        for i in self.modules:
            i.on_startup()
        self.broadcast("post_startup")

        # 6) Start tick
        self.initialize_tick()

    def __bootstrap__(self):
        """
        Run the bootstrap process for Juniper in the current program context
        """
        # 1) Check if the current program is enabled
        # ..

        # 2) Run bootstrap updates (pip packages)
        updater_source_path = os.path.join(self.workspace_root, "Source\\libs\\python\\juniper\\engine\\bootstrap\\updater.py")
        updater_module = SourceFileLoader("juniper.engine.bootstrap.updater", updater_source_path).load_module()
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

    def __tick__(self):
        """
        Runs the tick for Juniper
        """
        self.time_pf = self.time_cf
        self.time_cf = datetime.now()

        _delta = (self.time_cf - self.time_pf)
        self.delta_seconds = _delta.seconds + _delta.microseconds / 1E6

        for i in self.plugins:
            i.on_tick()
        for i in self.modules:
            i.on_tick()
        self.on_tick()

    def initialize_tick(self):
        """
        Binds the tick command to the host application
        Note: By default we use a Qt based QTimer - this may not work in all hosts
        for those hosts this method should be overriden
        """
        from qtpy import QtCore
        import juniper.widgets
        app = juniper.widgets.get_application()
        if(app):
            timer = QtCore.QTimer()
            timer.timeout.connect(self.__tick__)
            timer.start(0)
            self.__timer = timer

    # -------------------------------------------------------------------

    def shutdown(self):
        """
        Run the shutdown process for Juniper
        """
        self.__shutdown__()

    # -------------------------------------------------------------------

    def on_pre_startup(self):
        """
        Overrideable pre-startup method for host implementations
        """
        pass

    def on_startup(self):
        """
        Overrideable startup method for host implementations
        """
        pass

    def on_post_startup(self):
        """
        Overrideable post-startup method for host implementations
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

    def on_tick(self):
        """
        Overrideable tick method call each update
        """
        pass

    # -------------------------------------------------------------------

    def create_bootstrap_file(self, destination_path):
        """
        Creates a bootstrap path for the given program context - which is used to hook to Juniper startup in a given host application
        This is just the boilerplate class for bootstrapping. Depending on the host application the `bootstrap_call_lines` method
        may need to be overriden (some applications require a certain file / function setup to initialize plugins)
        :param <str:destination_path> The path to the bootstrap file
        """
        # 1) Boulerplate arguments (startup + context)
        file_lines = []
        file_lines.append("import sys\n")
        file_lines.append("sys.argv.append(\"juniper:startup=true\")\n")
        file_lines.append(f"sys.argv.append(\"juniper:program_context={self.program_context}\")\n")

        # 2) Add source lines in the bootstrap module
        bootstrap_source_lines = []
        bootstrap_module_path = os.path.join(self.workspace_root, "Source\\Libs\\Python\\juniper\\engine\\bootstrap\\__init__.py")
        with open(bootstrap_module_path, "r") as f:
            bootstrap_source_lines = f.readlines()
        file_lines += bootstrap_source_lines
        file_lines += "\n"  # fix for missing newlines at the end of bootstrap files

        # 3) Boilerplate code for calling bootstrap
        file_lines += [x + "\n" for x in self.bootstrap_call_lines()]

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
    @functools.lru_cache()
    def plugins(self):
        """
        :return <[Plugin]:plugins> Returns all registered plugins
        """
        import juniper.engine.bootstrap.types.plugin

        output = []
        for i in glob.glob(self.workspace_root + "\\Plugins\\**\\*.jplugin", recursive=True):
            plugin = juniper.engine.bootstrap.types.plugin.Plugin(i)
            if(plugin):
                output.append(plugin)

        return output

    @property
    @functools.lru_cache()
    def modules(self):
        """
        :return <[Module]:modules> Returns all registered modules
        """
        import juniper.engine.types.module
        return [x for x in juniper.engine.types.module.ModuleManager()]

    # -------------------------------------------------------------------

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

    def run_file(self, file_path):
        """
        Runs a script file in the current application
        Note: Override this in host applications to run bespoke file types as required
        :param <str:file_path> The path to the file to run
        :return <bool:success> True if the file was ran - else False
        """
        import juniper_globals

        if(os.path.isfile(file_path) and file_path.lower().endswith(".py")):
            globals_ = globals()
            globals_["__file__"] = file_path
            globals_["__package__"] = os.path.dirname(file_path)
            globals_["__name__"] = "__main__"
            juniper_globals.set("__juniper_exec_file_path__", file_path)
            exec(open(file_path).read(), globals_)
            return True
        return False

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
            for i in glob.iglob(plugin.root + "\\Source\\Scripts\\**\\*.*", recursive=True):
                script = juniper.engine.types.script.Script(i)
                if(script and script.get("type") == "script"):
                    output.append(script)

        for module in self.modules:
            for i in glob.iglob(module.root + "\\Source\\Scripts\\**\\*.*", recursive=True):
                script = juniper.engine.types.script.Script(i)
                if(script and script.get("type") == "script"):
                    output.append(script)

        return output

    @property
    def tools(self):
        """
        :return <[Script]:tools> All available tools in the current context
        """
        import juniper.engine.types.script
        output = []

        # Note: No core / host tools. The base implementations should be empty.

        for plugin in self.plugins:
            for i in glob.iglob(plugin.root + "\\Source\\Tools\\**\\*.*", recursive=True):
                script = juniper.engine.types.script.Script(i)
                if(script and script.get("type") == "tool"):
                    output.append(script)

        for module in self.modules:
            for i in glob.iglob(module.root + "\\Source\\Tools\\**\\*.*", recursive=True):
                script = juniper.engine.types.script.Script(i)
                if(script and script.get("type") == "tool"):
                    output.append(script)

        return output

    def find_tool(self, tool_name):
        """
        Finds a tool by its name
        :param <str:name> The name of the tool
        :return <Script:tool> The tool if found - else None
        """
        for i in self.tools:
            if(i.name == tool_name):
                return i
        return None

    def find_script(self, script_name):
        """
        Finds a script by its name
        :param <str:name> The name of the script
        :return <Script:tool> The script if found - else None
        """
        for i in self.scripts:
            if(i.name == script_name):
                return i
        return None

    # -------------------------------------------------------------------

    def get_qt_application(self):
        """
        Returns the QApplication instance - creates it if it has not been initialized
        :return <QApplication:out> The QApplication instance
        """
        from qtpy import QtWidgets
        import juniper.widgets.q_standalone_app
        output = QtWidgets.QApplication.instance()
        if(not output):
            return juniper.widgets.q_standalone_app.QStandaloneApp()
        return output

    def register_qt_widget(self, widget):
        """
        Used for certain host applications where a widget needs to be parented
        to a main window in a specific way
        :param <QWidget:widget> The widget to parent
        """
        pass

    def get_main_window(self):
        """
        Gets the main QMainWindow object for the current host application
        :return <QMainWindow:main_window> The main window object if found - else None
        """
        app = self.get_qt_application()  # by default just ensure the app is created
        if(hasattr(app, "main_window")):
            return app.main_window
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
        juniper_config = os.path.join(os.getenv("APPDATA"), "juniper\\config.json")
        if(os.path.isfile(juniper_config)):
            with open(juniper_config, "r") as f:
                try:
                    root = json.load(f)["path"]
                    if(os.path.isdir(root)):
                        return root
                except Exception:
                    pass
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

    @property
    def name(self):
        return self.__class__.__name__

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
        import juniper.engine.logging
        return juniper.engine.logging.Log(plugin="Juniper")

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
