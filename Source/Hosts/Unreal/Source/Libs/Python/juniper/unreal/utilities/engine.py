"""
Unreal Engine - Engine based utility functions
"""
import winreg

import juniper.utilities.pathing


def get_installed_engines():
    """
    Returns a dict containing info on all installed engines (as stored in the windows registry)
    :return <{str:str}:installed_engines> Formatted `{"engine_alias": "engine_root"}`
    """
    output = {}
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Epic Games\\Unreal Engine\\Builds') as key:
        _, num_entries, _ = winreg.QueryInfoKey(key)
        for i in range(num_entries):
            entry = winreg.EnumValue(key, i)
            name_ = entry[0]
            root = juniper.utilities.pathing.sanitize_path(entry[1])
            output[name_] = root
    return output


def find_engine_root(engine_association):
    """
    Finds the root directory for an engine from the name as stored in the registry
    :param <str:guid_string> The guid to search for
    :return <str:dir> The path to the engine root directory - None if not found
    """
    all_installed_engines = get_installed_engines()
    if(engine_association in all_installed_engines):
        return all_installed_engines[engine_association]
    return None
