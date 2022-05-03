"""
Standalone module used for various install/startup bootstrap functionality
"""
import importlib
import json
import os
import sys


def root():
    """
    :return <str:dir> The root director of Juniper relative to the bootstrap source file
    """
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "../../../"
    ))


def appdata_dir():
    """
    :return <str:dir> The root directory for Juniper data in "AppData/Roaming"
    """
    return os.path.join(os.getenv("APPDATA"), "Juniper")


def appdata_config_path():
    """
    :return <str:path> The base json config path for saved juniper user data
    """
    return os.path.join(appdata_dir(), "config.json")


def initialize_juniper_appdata():
    """
    Adds all required Juniper information to the config file in the users "AppData/Roaming"
    """
    juniper_data = {
        "path": root()
    }
    if(not os.path.isdir(appdata_dir())):
        os.makedirs(appdata_dir())
    with open(appdata_config_path(), "w") as f:
        f.writelines(json.dumps(juniper_data))


def initialize_juniper_libraries():
    """
    Adds all python libraries to the sys.path
    """
    for i in reversed(core_library_paths()):
        sys.path.insert(0, i)


def core_library_paths():
    """
    :return <[str]:dirs> The directories to all core/required python libraries
    """
    output = []

    output.append(os.path.join(root(), "Source\\Libs\\python"))
    output.append(os.path.join(root(), "Cached\\PyCache\\Python37\\site-packages"))  # TODO! Current host python version

    return output


def set_program_context(context):
    """
    Sets the current host program context
    """
    import juniper_globals
    juniper_globals.set("program_context", context or "python")


def get_program_context():
    """
    Gets the current host program context
    """
    import juniper_globals
    return juniper_globals.get("program_context")


def is_program_enabled(context):
    # TODO!
    return True


def run_file(file_path, program_context=None):
    path_ = file_path
    globals_ = globals()
    globals_["__file__"] = path_
    globals_["__package__"] = os.path.dirname(file_path)
    globals_["__program_context__"] = program_context or "python"
    exec(open(path_).read(), globals_)


def get_supported_host_program_names():
    output = []
    install_scripts_dir = os.path.join(root(), "Source\\Install")
    for i in os.listdir(install_scripts_dir):
        if(i.startswith("__install__.") and i.endswith(".py") and i.count(".") == 2):
            output.append(i.split(".")[1].lower())
    return output


def refresh_imports():
    """
    Refreshes the base juniper import
    """
    # We must reload the base module here as when we're in standalone Python mode
    # the stub 'juniper.py' module is used as a hook to run startup files.
    # After the core juniper paths have been added to sys.path we will no longer need this
    # and should instead import the actual juniper module.
    import juniper
    importlib.reload(juniper)

# -----------------------------------------------------------------------------

def install():
    # TODO!
    initialize_juniper_appdata()
    startup("python")

    for i in get_supported_host_program_names():
        install_script_path = os.path.join(root(), "Source\\Install", f"__install__.{i}.py")
        run_file(install_script_path)

    # Plugin install scripting
    import juniper.framework.backend.plugin
    import juniper.utilities.script_execution

    for i in (None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
        for plugin in juniper.framework.backend.plugin.PluginManager():
            if(plugin.enabled):
                install_scripts = plugin.install_scripts(i)
                for script_path in install_scripts:
                    juniper.utilities.script_execution.run_file(script_path)

def startup(program_context):
    # TODO!
    if(is_program_enabled(program_context)):
        initialize_juniper_libraries()
        set_program_context(program_context)

        refresh_imports()  # from here we can use all base juniper libraries

        # Check pip package hash
        # ..

        # Initialize macros before startup so they can be accessed if needed
        import juniper.framework.backend.plugin

        for plugin in juniper.framework.backend.plugin.PluginManager():
            if(plugin.enabled):
                plugin.initialize_libraries()
                plugin.initialize_macros()

        # Plugin startup scripting
        import juniper.utilities.script_execution

        for i in (None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
            for plugin in juniper.framework.backend.plugin.PluginManager():
                if(plugin.enabled):
                    startup_scripts = plugin.startup_scripts(i)
                    for script_path in startup_scripts:
                        juniper.utilities.script_execution.run_file(script_path)
