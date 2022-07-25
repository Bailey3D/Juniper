"""
TODO! Delete / replace methods
Standalone module used for various install/startup bootstrap functionality
Note: This module should not depend on any external/third-party libraries until after `startup()` has ran (including Juniper)
"""
import functools
import hashlib
import json
import os
import pathlib
import shutil
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


def python_path():
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

    # Some programs might have a non-standard folder structure
    # Blender is the only one I've came across. We may need more edge cases depending on the host
    if(not output):
        check_dir = os.path.dirname(os.__file__)
        while(not output and len(check_dir) > 3):
            possible_exe_path = os.path.join(check_dir, "bin\\python.exe")
            if(os.path.isfile(possible_exe_path)):
                output = possible_exe_path
            else:
                check_dir = os.path.dirname(check_dir)

    return output


# -------------------------------------------------------


def requirements_txt_path():
    """
    :return <str:path> The path to the `requirements.txt` file as stored in config
    """
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
        python_path_resolved = pathlib.Path(python_path()).resolve()
        requirements_txt_path_resolved = pathlib.Path(requirements_txt_path()).resolve()
        pip_whl_path = pathlib.Path(os.path.join(root(), "Binaries\\Python\\py3-none-any.whl"))

        # Setuptools can't be guarenteed to have been installed in all the host contexts
        # so install this first
        cmd = f""""{python_path_resolved}" "{pip_whl_path}/pip" install setuptools -t {site_packages_dir}""".replace("\\", "/")
        _ = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        # TODO~ We need a way to prompt the user of an error on pip install
        cmd = f""""{python_path_resolved}" "{pip_whl_path}/pip" install -r "{requirements_txt_path_resolved}" -t "{site_packages_dir}" """
        cmd = cmd.replace("\\", "/")
        _ = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        #  print(result.returncode, result.stdout, result.stderr)

        # Copy the Python3.dll to the shiboken2 directory in site packages
        # this will fix the issues with launching PySide2 within certain applications
        # (blender is the only known application that has this issue..)
        shiboken_site_packages_dir = os.path.join(site_packages_dir, "shiboken2")
        dll_path = os.path.join(
            os.path.dirname(python_path()),
            "python3.dll"
        )
        if(os.path.isfile(dll_path) and os.path.isdir(shiboken_site_packages_dir)):
            shutil.copyfile(dll_path, os.path.join(shiboken_site_packages_dir, "python3.dll"))

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
        "..\\..\\..\\..\\..\\"
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
    # Insert the base juniper libraries so they are first found (before any bootstrap libraries)
    sys.path.insert(0, os.path.join(root(), "Source\\Libs\\python"))
    # Insert to the end, to ensure any inbuilt libraries are prioritised over Juniper pip installs
    sys.path.append(os.path.join(root(), f"Cached\\PyCache\\Python{python_version_major()}{python_version_minor()}\\site-packages"))


def set_program_context(context):
    """
    Sets the current host program context
    """
    import juniper_globals
    juniper_globals.set("program_context", context or "python")


def is_program_enabled(context):
    # TODO~ We need a way to enable/disable program integrations + a GUI
    return True


def run_file(file_path):
    """
    Runs a file from its path
    :param <str:file_path> The path to the file to run
    """
    path_ = file_path
    globals_ = globals()
    globals_["__file__"] = path_
    globals_["__package__"] = os.path.dirname(file_path)
    exec(open(path_).read(), globals_)


def get_supported_host_program_names():
    """
    Gets the names of all supported hosts
    :return <[str]:hosts> The names of all supported hosts
    """
    output = []
    host_plugins_dir = os.path.join(root(), "Plugins\\JuniperHosts")
    for i in os.listdir(host_plugins_dir):
        host_plugin_dir = os.path.join(host_plugins_dir, i)
        for i in os.listdir(host_plugin_dir):
            if(i.endswith(".jplugin")):
                output.append(i.split(".")[0])
    return sorted(output)

# -----------------------------------------------------------------------------


def install():
    """
    Runs the install process for Juniper
    """
    from importlib.machinery import SourceFileLoader
    juniper_engine_module = SourceFileLoader(
        "juniper.engine",
        os.path.join(root(), "Source\\libs\\python\\juniper\\engine\\__init__.py")
    ).load_module()
    juniper_engine_module.JuniperEngine(install=True)


def startup(program_context):
    """
    Runs the startup process for juniper
    """
    #program_context = "blender"
    if(program_context != "python"):
        sys.path.append(os.path.join(root(), "Source\\Libs\\python"))
        hosts_dir = os.path.join(root(), "Source\\Hosts")
        for i in os.listdir(hosts_dir):
            if(i.lower() == program_context):
                plugin_path = os.path.join(hosts_dir, i, "Source\\__plugin__.py")
                from importlib.machinery import SourceFileLoader
                juniper_engine_module = SourceFileLoader(
                    "juniper.engine_override",
                    plugin_path
                ).load_module()
                cls = eval(f"juniper_engine_module.{program_context.capitalize()}")
                cls(startup=True)
                #juniper_engine_module.JuniperEngine(startup=True)
    else:
        from importlib.machinery import SourceFileLoader
        juniper_engine_module = SourceFileLoader(
            "juniper.engine",
            os.path.join(root(), "Source\\libs\\python\\juniper\\engine\\__init__.py")
        ).load_module()
        juniper_engine_module.JuniperEngine(startup=True)
