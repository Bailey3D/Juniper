"""
Adds an extra directory to the plugins search location during startup
"""
try:
    import juniper
except Exception:
    raise Exception("Unable to run script `add_plugin_search_directory.py` as Juniper is not installed.\n\
                    Please run `/Binaries/Juniper/Install.bat` first!")

import juniper.engine.paths
import juniper.utilities.filemgr

import json
import os


search_dir = juniper.utilities.filemgr.pick_folder("Pick Plugin Search Folder..", start=juniper.engine.paths.root())

if(search_dir and os.path.isdir(search_dir)):
    user_settings_json_file = os.path.join(juniper.engine.paths.root(), "Cached\\UserConfig\\user_settings.json")

    if(os.path.isfile(user_settings_json_file)):
        with open(user_settings_json_file, "r") as f:
            json_data = json.load(f)
    else:
        json_data = {}

    if("juniper" not in json_data):
        json_data["juniper"] = {}

    if("extra_plugin_search_directories" not in json_data["juniper"]):
        json_data["juniper"]["extra_plugin_search_directories"] = []

    if(search_dir not in json_data["juniper"]["extra_plugin_search_directories"]):
        json_data["juniper"]["extra_plugin_search_directories"].append(search_dir)

    with open(user_settings_json_file, "w") as f:
        json.dump(json_data, f, indent=4, sort_keys=True)

    juniper.log.success(f"Added extra plugin search directory: {search_dir}")

else:
    juniper.log.success("Adding extra plugin search directory cancelled by user.")
