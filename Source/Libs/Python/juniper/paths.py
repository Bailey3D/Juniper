"""
Library used for path based functions for juniper
"""
import os
import functools
import ctypes
import ctypes.wintypes

import juniper.utilities.json as json_utils


@functools.lru_cache()
def root():
    """Returns the path to the juniper as stored in the registry\n
    :return <str:path> Registry path\n
    """
    return json_utils.get_property(os.path.join(os.getenv("APPDATA"), "juniper\\config.json"), "path")


# --------------------------------------------------------------------------------------

def get_override_path(filepath, override):
    filename, _, filetype = filepath.rpartition(".")
    if(not filepath.endswith(f"{override}.{filetype}")):
        return f"{filename}.{override}.{filetype}"
    return filepath


def __find_file(subdir, relative_path, override=None, plugin=None):
    import juniper.framework.backend.plugin
    output = None
    plugin = None if not plugin else juniper.framework.backend.plugin.PluginManager().find_plugin(plugin)

    # Plugin + Override / Plugin - Override
    if(plugin):
        output = plugin.get_file(subdir, relative_path, override=override)

    # Override
    if(override and not output):
        possible_output = os.path.join(root(), subdir, get_override_path(relative_path, override))
        if(os.path.isfile(possible_output)):
            output = possible_output

    # Base
    if(not output):
        possible_output = os.path.join(root(), subdir, relative_path)
        if(os.path.isfile(possible_output)):
            output = possible_output

    return output


def find_config(relative_path, override=None, plugin=None):
    return __find_file("config", relative_path, override=override, plugin=plugin)


def find_resource(relative_path, override=None, plugin=None):
    return __find_file("resources", relative_path, override=override, plugin=plugin)


# --------------------------------------------------------------------------------------


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


def site_packages_dir():
    import juniper.framework.versioning
    return os.path.join(
        juniper.paths.root(),
        f"lib\\external\\python{juniper.framework.versioning.python_version()}\\site-packages"
    )


# --------------------------------------------------------------------------------------

def documents():
    """
    :return <str:dir> Path to the current users documents directory
    """
    CSIDL_PERSONAL = 5
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    return str(buf.value)


def local_appdata():
    """
    :return <str:path> The path to the users Local Appdata directory
    """
    return os.getenv("LOCALAPPDATA")
