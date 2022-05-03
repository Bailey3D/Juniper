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


def _get_path(path, dir_, program=None, module=None):
    """Returns the path to a Juniper directory file
    :param <str:path> The config dir relative path to the file directory
    :param <str:dir_> The directory to search inside of
    :param [<str:program>] The program context (Ie, "Max")
    :param [<str:module>] The module context (Ie, "asset_library")
    """
    import juniper.framework.backend.module
    output = ""

    if(module):
        module_ref = juniper.framework.backend.module.ModuleManager.find(module)
        module_root = module_ref.module_root

    if(program is None):
        import juniper.framework.backend.program
        program = juniper.framework.backend.program.program_context()

    if(None not in (program, module)):
        # both program and module are specified
        output = os.path.join(module_root, dir_, program, path)

    if(not os.path.isfile(output) and module):
        # just module specified (search module common)
        output = os.path.join(module_root, dir_, "common", path)

    if(not os.path.isfile(output) and program):
        # just program specified
        output = os.path.join(root(), dir_, program, path)

    if(not os.path.isfile(output)):
        output = os.path.join(root(), dir_, "common", path)

    return output


def get_config(path, program=None, module=None):
    """Returns the path to a Juniper config file
    :param <str:path> The config dir relative path to the file
    :param [<str:program>] The program context (Ie, "Max")
    :param [<str:module>] The module context (Ie, "AssetLibrary")
    """
    return _get_path(path, "config", program=program, module=module)


def get_resource(path, program=None, module=None):
    """Returns the path to a Juniper resource file
    :param <str:path> The config dir relative path to the file
    :param [<str:program>] The program context (Ie, "Max")
    :param [<str:module>] The module context (Ie, "AssetLibrary")
    """
    return _get_path(path, "resources", program=program, module=module)


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


@functools.lru_cache()
def module_dirs(include_internal=True, include_external=True):
    """Gets a list containing paths to all Juniper module directories\n
    :return <[str]:path> List of paths to the module roots\n
    """
    output = []

    # externally added modules
    if(include_external):
        external_modules_dict = json_utils.get_property(get_config("client_settings.json"), "external_modules")
        for i in external_modules_dict:
            if(external_modules_dict[i] not in output):
                output.append(external_modules_dict[i])

    # external modules in modules directory
    if(include_external):
        external_modules_dir = os.path.join(root(), "modules\\external")
        if(os.path.isdir(external_modules_dir)):
            for i in os.listdir(external_modules_dir):
                possible_dir = os.path.join(external_modules_dir, i)
                if(os.path.isdir(possible_dir) and possible_dir not in output):
                    output.append(possible_dir)

    # inbuilt modules
    if(include_internal):
        internal_modules_dir = os.path.join(root(), "modules\\internal")
        if(os.path.isdir(internal_modules_dir)):
            for i in os.listdir(internal_modules_dir):
                possible_dir = os.path.join(internal_modules_dir, i)
                if(os.path.isdir(possible_dir) and possible_dir not in output):
                    output.append(possible_dir)

    return output


@functools.lru_cache(maxsize=8)
def get_module_root(module_name):
    """Gets the directory path for a given module
    :param <str:module_name> Name of the module to find
    """
    module_name = module_name.lower()
    for i in module_dirs():
        if(os.path.basename(i).lower() == module_name):
            return i
        else:
            if(os.path.isfile(os.path.join(i, module_name + ".jmodule"))):
                return i
    return ""


def get_path(path, module_name=None):
    """Converts a module/juniper relative path to an absolute path if it exists.
    :param <str:path> Relative path to convert
    :param [<str:module_name>] Optional name of the module to get
    :return <str:path> Absolute path if found "" if not
    """
    if(os.path.isfile(path)):
        return path

    output = path

    if(not os.path.isfile(output) and module_name):
        output = os.path.join(get_module_root(module_name), path)
        if(os.path.isfile(output)):
            return output

    output = os.path.join(root(), path)
    if(os.path.isfile(output)):
        return output

    return ""


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
