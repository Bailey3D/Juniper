import json
import os
import shutil

import juniper.plugins
import unreal.juniper
import juniper.paths
import juniper.utilities.filemgr
import juniper.utilities.json as json_utils


class UnrealInstaller(object):
    def __init__(self):
        self.install()

    @property
    def unreal_project_path(self):
        output = unreal.juniper.unreal_project_path()

        if(output):
            start_dir = os.path.dirname(output)
        else:
            start_dir = juniper.paths.root()

        picked_path = juniper.utilities.filemgr.pick_file(
            title="Select Target Unreal Project..",
            file_types="Unreal Project (*uproject)",
            start=start_dir
        ).replace("/", "\\")

        if(picked_path and os.path.isfile(picked_path)):
            output = picked_path

        return output

    @property
    def plugin(self):
        return juniper.plugins.PluginManager().find_plugin("unreal")

    def install(self):
        unreal_project_path = self.unreal_project_path
        if(unreal_project_path and os.path.isfile(unreal_project_path)):
            unreal_project_dir = os.path.dirname(unreal_project_path)

            # Generate the user settings json if it doesn't exist
            user_settings_path = os.path.join(juniper.paths.root(), "Cached\\UserConfig\\user_settings.json")
            if(not os.path.isfile(user_settings_path)):
                os.makedirs(os.path.dirname(user_settings_path))
                with open(user_settings_path, "w") as f:
                    json.dump({}, f)

            # Set the unreal project path
            json_utils.set_file_property(
                os.path.join(juniper.paths.root(), "Cached\\UserConfig\\user_settings.json"),
                "unreal_project_path",
                unreal_project_path,
                local=False
            )

            # Copy the bootstrap script to the Unreal project's Python startup directory
            startup_script = os.path.join(self.plugin.root, "Source\\Bootstrap\\__bootstrap__.py")
            target_path = os.path.join(unreal_project_dir, "content\\Python\\Startup\\Juniper\\__bootstrap__.py")
            if(not os.path.isdir(os.path.dirname(target_path))):
                os.makedirs(os.path.dirname(target_path))
            shutil.copyfile(startup_script, target_path)

            # Add the startup script line to the "DefaultEngine.ini"
            # We add this to the "/content/Python/" folder
            default_engine_ini_path = os.path.join(unreal_project_dir, "Config\\DefaultEngine.ini")
            python_plugin_start_line_string = "[/Script/PythonScriptPlugin.PythonScriptPluginSettings]"
            startup_script_string = "+StartupScripts=startup/juniper/__bootstrap__.py"

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


UnrealInstaller()
