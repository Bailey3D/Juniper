import os
import shutil

import juniper.paths


if(os.path.isdir(juniper.paths.root())):
    blender_dir = "c:\\users\\" + os.getlogin() + "\\Appdata\\Roaming\\Blender Foundation\\Blender"

    for i in os.listdir(blender_dir):
        blender_sub_dir = os.path.join(blender_dir, i)
        if(os.path.isdir(blender_sub_dir) and (i.replace(".", "").isdigit())):
            startup_folder = os.path.join(blender_sub_dir, "scripts\\startup")
            startup_script = os.path.join(juniper.paths.root(), "Source\\Startup\\__startup__.blender.py")
            if(not os.path.isdir(startup_folder)):
                os.makedirs(startup_folder)
            shutil.copyfile(startup_script, os.path.join(startup_folder, "__juniper_startup__.py"))
