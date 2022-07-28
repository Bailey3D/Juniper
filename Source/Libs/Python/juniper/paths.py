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
    """
    Returns the path to the juniper as stored in the registry
    :return <str:path> Registry path
    """
    return json_utils.get_property(os.path.join(os.getenv("APPDATA"), "juniper\\config.json"), "path")


# --------------------------------------------------------------------------------------

def get_override_path(filepath, override):
    """
    Gets a file path with an extra override type (Ie, "file.txt.override")
    :param <str:filepath> The path to the file
    :param <str:override> The override file type
    :return <str:override_path> The override file path
    """
    filename, _, filetype = filepath.rpartition(".")
    if(not filepath.endswith(f"{override}.{filetype}")):
        return f"{filename}.{override}.{filetype}"
    return filepath


def __find_file(subdir, relative_path, override=None, plugin=None):
    import juniper.engine.types.plugin
    output = None
    plugin = None if not plugin else juniper.engine.types.plugin.PluginManager().find_plugin(plugin)

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
