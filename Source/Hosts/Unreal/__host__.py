"""
Base implementation for Juniper support in Unreal Engine
Currently only a single project is supported at a time.
"""
import json
import os

import juniper.engine


class Unreal(juniper.engine.JuniperEngine):
    def get_host_module_names(self):
        return ("unreal",)

    def on_install(self):
        """
        Installs Juniper bootstrap to a target unreal project
        :TODO~ Juniper Engine: UProject wrapper class, find the current uproject from the current python instance
        """
        import juniper.utilities.filemgr

        unreal_project_path = self.__current_unreal_project_path
        if(not unreal_project_path or not os.path.isfile(unreal_project_path)):
            unreal_project_path = self.__pick_unreal_project_path()

        if(unreal_project_path):
            unreal_project_dir = os.path.dirname(unreal_project_path)

            # Generate user settings json if it doesn't exist
            if(not os.path.isfile(self.__user_settings_json_path)):
                os.makedirs(os.path.dirname(self.__user_settings_json_path))
                with open(self.__user_settings_json_path, "w") as f:
                    json.dump({}, f)

            # Get the current user settings data
            with open(self.__user_settings_json_path, "r") as f:
                json_data = json.load(f)

            # Set the unreal project path
            json_data["unreal_project_path"] = unreal_project_path
            with open(self.__user_settings_json_path, "w") as f:
                json.dump(json_data, f)

            # Create bootstrap
            bootstrap_path = os.path.join(unreal_project_dir, "Content\\Python\\Startup\\Juniper\\__bootstrap__.py")
            juniper.utilities.filemgr.remove_read_only(bootstrap_path)
            self.create_bootstrap_file(bootstrap_path)

            # Add the startup script line to the "DefaultEngine.ini"
            # We add this to the "/content/python/" directory
            ini_path = self.__default_engine_ini_path
            python_plugin_lines = "[/Script/PythonScriptPlugin.PythonScriptPluginSettings]"
            startup_script_string = "+StartupScripts=startup/juniper/__bootstrap__.py"

            juniper.utilities.filemgr.remove_read_only(ini_path)

            if(os.path.isfile(ini_path)):
                with open(ini_path, "r") as f:
                    ini_data = f.read()

                with open(ini_path, "w") as f:
                    if(python_plugin_lines in ini_data):
                        if(startup_script_string not in ini_data):
                            ini_data = ini_data.replace(
                                python_plugin_lines,
                                python_plugin_lines + "\n" + startup_script_string
                            )
                    else:
                        ini_data += str(
                            "\n" + python_plugin_lines + "\n" + startup_script_string
                        )
                    f.write(ini_data)

    def on_shutdown(self):
        try:
            import unreal
            unreal.unregister_slate_post_tick_callback(self.slate_tick_handle)
            unreal.unregister_python_shutdown_callback(self.engine_shutdown_handle)        
        except Exception:
            pass

    def initialize_tick(self):
        import unreal

        def slate_tick(delta_seconds):
            self.__tick__()

        self.slate_tick_handle = unreal.register_slate_post_tick_callback(slate_tick)

    def on_post_startup(self):
        import unreal
        self.engine_shutdown_handle = unreal.register_python_shutdown_callback(self.on_shutdown)

    def register_qt_widget(self, widget):
        import unreal
        unreal.parent_external_window_to_slate(
            widget.winId(),
            unreal.SlateParentWindowSearchMethod.ACTIVE_WINDOW
        )

    # --------------------------------------------------------------------

    @property
    def __default_engine_ini_path(self):
        if(self.__current_unreal_project_path):
            return os.path.join(
                os.path.dirname(self.__current_unreal_project_path),
                "Config\\DefaultEngine.ini"
            )

    @property
    def __user_settings_json_path(self):
        return os.path.join(self.workspace_root, "Cached\\UserConfig\\user_settings.json")

    @property
    def __current_unreal_project_path(self):
        if(os.path.isfile(self.__user_settings_json_path)):
            with open(self.__user_settings_json_path, "r") as f:
                json_data = json.load(f)
                if("unreal_project_path" in json_data):
                    return json_data["unreal_project_path"]
        return None

    def __pick_unreal_project_path(self):
        import juniper.utilities.filemgr

        output = self.__current_unreal_project_path

        if(output):
            start_dir = os.path.dirname(output)
        else:
            start_dir = self.workspace_root

        picked_path = juniper.utilities.filemgr.pick_file(
            title="Select Target Unreal Project..",
            file_types="Unreal Project (*uproject)",
            start=start_dir
        ).replace("/", "\\")

        if(picked_path and os.path.isfile(picked_path)):
            output = picked_path

        return output
