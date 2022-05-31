"""
Content browser based functions
"""
import os

import juniper_globals
import juniper.utilities.pathing as pathing_utils


def register_unreal_content_dir(directory, alias):
    """
    Registers an unreal content dir with an alias.
    Used primarily to map absolute paths to be relative to the Unreal content browser.
    ```
    example_path = "c:\\example\\path.txt"
    register_unreal_content_dir("c:\\example", "/SomeAlias/")
    map_path(example_path) # "c:\\example\\path.txt" -> "/SomeAlias/path"
    ```
    :param <str:directory> The real directory to add a mapping for
    :param <str:alias> Relative path alias
    """
    directory = pathing_utils.sanitize_path(directory)
    directory = directory.lower()

    registered_dirs = juniper_globals.get("registered_unreal_content_dirs")
    if(registered_dirs is None):
        registered_dirs = {}
    registered_dirs[directory] = alias

    juniper_globals.set("registered_unreal_content_dirs", registered_dirs)

    return True


def get_registered_unreal_content_dirs():
    """
    :return <{str:str}:dirs> Registered directories - see `register_unreal_content_dir` for more info.
    """
    output = juniper_globals.get("registered_unreal_content_dirs")
    if(output is None):
        juniper_globals.set("registered_unreal_content_dirs", {})
        output = {}
    return output


def map_path(path, remove_suffix=True):
    """
    Maps an absolute path to be relative to a registered unreal content directory
    :param <str:path> The absolute path to map
    :param [<bool:remove_suffix>] Should the file type be removed? Unreal doesn't use these as everything should be .uasset
    :return <str:mapped> The mapped path - None if not mapped
    """
    path = pathing_utils.sanitize_path(path)
    registered_content_dirs = get_registered_unreal_content_dirs()
    for i in registered_content_dirs:
        if(path.lower().startswith(i)):
            alias = registered_content_dirs[i]
            output = f"{alias}{path[len(i):]}"
            output = output.replace("\\", "/")  # Unreal requires "/"
            output = output.replace("//", "/")
            if(remove_suffix):
                output = os.path.splitext(output)[0]
            return output
    return None


def save_asset(asset_object, force=False):
    """
    Save a material UAsset
    :param <UObject:asset_object> The asset to save
    :param [<bool:force>] Should this be saved even if not updated?
    """
    import unreal
    unreal.EditorAssetLibrary.save_loaded_asset(asset_object, only_if_is_dirty=force)
