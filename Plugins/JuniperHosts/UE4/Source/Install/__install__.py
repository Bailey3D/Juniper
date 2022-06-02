import json
import os
import shutil

import juniper.plugins
import juniper_ue4
import juniper.paths
import juniper.utilities.filemgr
import juniper.utilities.json as json_utils


# pick the current unreal project
uproj_path = juniper.utilities.filemgr.pick_file(
    title="Select Target Unreal Project",
    file_types="Unreal Project (*.uproject)",
    start=juniper_ue4.unreal_project_dir()
)

uproj_path = uproj_path.replace("/", "\\")

if(os.path.isfile(uproj_path)):
    user_settings_path = os.path.join(juniper.paths.root(), "Cached\\UserConfig\\user_settings.json")
    if(not os.path.isfile(user_settings_path)):
        os.makedirs(os.path.dirname(user_settings_path))
        with open(user_settings_path, "w") as f:
            json.dump({}, f)

    json_utils.set_file_property(
        os.path.join(juniper.paths.root(), "Cached\\UserConfig\\user_settings.json"),
        "unreal_project_path",
        uproj_path,
        local=False
    )

    unreal_project_root = juniper_ue4.unreal_project_dir()

    # copy the "programs/unreal/lib/python/install/scripts/__startup__.py/" to the unreal project
    plugin = juniper.plugins.PluginManager().find_plugin("ue4")
    startup_script = os.path.join(plugin.root, "Source\\Bootstrap\\__bootstrap__.py")
    target_path = os.path.join(unreal_project_root, "content\\Script\\Editor\\Startup\\Juniper\\juniper.py")
    if(not os.path.isdir(os.path.dirname(target_path))):
        os.makedirs(os.path.dirname(target_path))
    shutil.copyfile(startup_script, target_path)

    # Add the startup script line to the "DefaultEngine.ini"
    # We add this to the "/content/script/" folder rather than "/content/python/"
    # (somewhat selfishly as I am using the UnLua plugin which uses "/content/script/" for its scripts!)
    default_engine_ini_path = os.path.join(unreal_project_root, "Config\\DefaultEngine.ini")
    python_plugin_start_line_string = "[/Script/PythonScriptPlugin.PythonScriptPluginSettings]"
    startup_script_string = "+StartupScripts=startup/juniper/juniper.py"

    if(os.path.isfile(default_engine_ini_path)):
        with open(default_engine_ini_path) as file:
            ini_file_data = file.read()

        with open(default_engine_ini_path, "w") as file:
            if(python_plugin_start_line_string in ini_file_data):
                if(startup_script_string not in ini_file_data):
                    ini_file_data = ini_file_data.replace(
                        python_plugin_start_line_string,
                        python_plugin_start_line_string + "\n" + startup_script_string
                    )
            else:
                ini_file_data += str(
                    "\n" + python_plugin_start_line_string + "\n" + startup_script_string
                )
            file.write(ini_file_data)
