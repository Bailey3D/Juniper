"""
Base implementation for Juniper support in Blender
"""
import os

import juniper.engine


class Blender(juniper.engine.JuniperEngine):
    def get_host_module_names(self):
        return ("bpy",)

    def on_install(self):
        """
        Install the Juniper bootstrap to Blender
        """
        blender_dir = "c:\\users\\" + os.getlogin() + "\\Appdata\\Roaming\\Blender Foundation\\Blender"

        for i in os.listdir(blender_dir):
            blender_sub_dir = os.path.join(blender_dir, i)
            if(os.path.isdir(blender_sub_dir) and (i.replace(".", "").isdigit())):
                startup_folder = os.path.join(blender_sub_dir, "scripts\\startup")
                self.create_bootstrap_file(os.path.join(startup_folder, "__juniper_startup__.py"))

    @property
    def python_path(self):
        """
        Blender uses a nonstandard Python folder structure for some reason, so we need an
        override for how to find the exe
        :return <str:path> The path to the Blender Python.exe
        """
        output = None
        check_dir = os.path.dirname(os.__file__)
        while(not output and len(check_dir) > 3):
            possible_exe_path = os.path.join(check_dir, "bin\\python.exe")
            if(os.path.isfile(possible_exe_path)):
                output = possible_exe_path
            else:
                check_dir = os.path.dirname(check_dir)
        return output
