"""
Standalone module used for various install/startup bootstrap functionality
Note: This module should not depend on any external/third-party libraries until after `startup()` has ran (including Juniper)
"""
import functools
import glob
import hashlib
import importlib
import json
import os
import pathlib
import sys
from subprocess import PIPE, run


def python_version():
    """
    Return the python version (Major.Minor ONLY)
    :return <float:version> Formatted MAJOR.MINOR (Ie, 3.7)
    """
    return float(f"{sys.version_info[0]}.{sys.version_info[1]}")


def python_version_major():
    """
    :return <int:major> Returns the python major version (Ie, 3)
    """
    return int(str(python_version()).split(".")[0])


def python_version_minor():
    """
    :return <int:minor> Returns the python minor version (Ie, 10)
    """
    return int(str(python_version()).split(".")[1])


def python_exe_path():
    """
    Gets the path to the current host Python exe
    We cannot rely on `sys.executable` as it will return the host application exe when using embedded Python (Ie, unreal.exe)
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


# -------------------------------------------------------


def requirements_txt_path():
    return os.path.join(root(), "Config\\Python\\requirements.txt")


def install_pip_packages(force=False):
    """
    Installs the pip packages in "Config\\Python\\requirements.txt" for the current host Python version (Major/Minor)
    Note: We must use `pathlib.Path("Some/Path").resolve()` as pip can fail to install on subst drives
    """
    cached_requirements_hash = requirements_hash(cached=True)
    current_requirements_hash = requirements_hash(cached=False, update=False)
    site_packages_dir = pathlib.Path(os.path.join(
        root(),
        f"Cached\\PyCache\\Python{python_version_major()}{python_version_minor()}\\site-packages"
    )).resolve()

    if(
        not cached_requirements_hash or
        cached_requirements_hash != current_requirements_hash or
        not os.path.isdir(site_packages_dir) or
        not len(os.listdir(site_packages_dir)) or
        force
    ):
        python_exe_path_resolved = pathlib.Path(python_exe_path()).resolve()
        requirements_txt_path_resolved = pathlib.Path(requirements_txt_path()).resolve()
        pip_whl_path = pathlib.Path(os.path.join(root(), "Binaries\\Python\\py3-none-any.whl"))

        # Setuptools can't be guarenteed to have been installed in all the host contexts
        # so install this first
        cmd = f""""{python_exe_path_resolved}" "{pip_whl_path}/pip" install setuptools -t {site_packages_dir}""".replace("\\", "/")
        result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        # TODO~ We need a way to prompt the user of an error on pip install
        cmd = f""""{python_exe_path_resolved}" "{pip_whl_path}/pip" install -r "{requirements_txt_path_resolved}" -t "{site_packages_dir}" """.replace("\\", "/")
        result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        #print(result.returncode, result.stdout, result.stderr)

        requirements_hash(cached=False, update=True)


def requirements_hash(cached=False, update=True):
    """
    Gets a hash of the requirements.txt - either from the file or cached version
    :param [<bool:cached>] If true the cached version is retrieved
    :param [<bool:update>] Should the cache be updated?
    :return <str:hash> The file hash as a string - None if invalid
    """
    output = None
    python_key = f"Python{python_version_major()}{python_version_minor()}"
    requirements_hash_cache_path = os.path.join(root(), "Cached\\PyCache\\requirements_hashes.json")

    # get cache json data or an empty version if not set
    if(os.path.isfile(requirements_hash_cache_path)):
        with open(requirements_hash_cache_path, "r") as f:
            json_data = json.load(f)
    else:
        json_data = {}

    # if only getting frmo cache, skip the rest
    if(cached):
        if(python_key in json_data):
            output = json_data[python_key]

    # for writing to the cache / updating
    else:
        BLOCK_SIZE = 65536
        file_hash = hashlib.sha256()
        with open(requirements_txt_path(), 'rb') as f:
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(BLOCK_SIZE)
        output = str(file_hash.hexdigest())
        if(update):
            json_data[python_key] = output
            if(not os.path.isdir(os.path.dirname(requirements_hash_cache_path))):
                os.makedirs(os.path.dirname(requirements_hash_cache_path))
            with open(requirements_hash_cache_path, "w") as f:
                json.dump(json_data, f)

    return output

# -------------------------------------------------------


@functools.lru_cache()
def root():
    """
    :return <str:dir> The root director of Juniper relative to the bootstrap source file
    """
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "..\\..\\..\\..\\"
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


def core_library_paths():
    """
    :return <[str]:dirs> The directories to all core/required python libraries
    """
    output = []

    output.append(os.path.join(root(), "Source\\Libs\\python"))
    output.append(
        os.path.join(root(), f"Cached\\PyCache\\Python{python_version_major()}{python_version_minor()}\\site-packages")
    )

    return output

# -------------------------------------------------------


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
        if(i not in sys.path):
            sys.path.insert(0, i)


def set_program_context(context):
    """
    Sets the current host program context
    """
    import juniper_globals
    juniper_globals.set("program_context", context or "python")


def is_program_enabled(context):
    # TODO~ We need a way to enable/disable program integrations + a GUI
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
    host_plugins_dir = os.path.join(root(), "Plugins\\JuniperHosts")
    for i in os.listdir(host_plugins_dir):
        host_plugin_dir = os.path.join(host_plugins_dir, i)
        for i in os.listdir(host_plugin_dir):
            if(i.endswith(".jplugin")):
                output.append(i.split(".")[0])
    return sorted(output)


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
    """
    Runs the install process for Juniper
    """
    initialize_juniper_appdata()
    startup("python")

    # Plugin install scripting
    import juniper
    import juniper.plugins
    import juniper.utilities.script_execution

    for i in (None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
        for plugin in juniper.plugins.PluginManager():
            if(plugin.enabled):
                install_scripts = plugin.install_scripts(i)
                for script_path in install_scripts:
                    juniper.log.info(f"Running Install Script: {script_path}", silent=True, context="Juniper - Install")
                    juniper.utilities.script_execution.run_file(script_path)


def startup(program_context):
    """
    Runs the startup process for juniper
    """
    if(is_program_enabled(program_context)):
        initialize_juniper_libraries()
        set_program_context(program_context)
        install_pip_packages()  # Check pip package hash and update if needed

        # From here we can use all base juniper libraries
        # but the macros / startup process will not be complete
        refresh_imports()

        # Initialize macros before startup so they can be accessed if needed
        import juniper.framework.tooling.macro
        for file in glob.iglob(os.path.join(juniper.paths.root(), "Source\\Tools\\**"), recursive=True):
            if(juniper.framework.tooling.macro.MacroManager.check_if_file_is_macro(file)):
                m = juniper.framework.tooling.macro.Macro(file, plugin="juniper")
                m.plugin = "juniper"
                juniper.framework.tooling.macro.MacroManager.register_macro(m)

        import juniper.plugins
        for plugin in juniper.plugins.PluginManager():
            if(plugin.enabled):
                plugin.initialize_libraries()
                plugin.initialize_macros()

        import juniper
        juniper.initialize_log()

        # Plugin startup scripting
        import juniper.utilities.script_execution

        for i in (None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
            for plugin in juniper.plugins.PluginManager():
                if(plugin.enabled):
                    startup_scripts = plugin.startup_scripts(i)
                    for script_path in startup_scripts:
                        juniper.log.info(f"Running Script: {script_path}", silent=True, context="Juniper - Startup")
                        juniper.utilities.script_execution.run_file(script_path)
