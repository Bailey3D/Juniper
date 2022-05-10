import os

import juniper
import juniper_designer
import juniper.plugins


class DesignerInstaller(object):
    def __init__(self):
        if(not os.path.isdir(self.local_sbsprj_dir)):
            os.makedirs(self.local_sbsprj_dir)

        # Read the template sbsprj
        shelf_lines = []
        with open(self.sbsprj_template_path, "r") as f:
            shelf_lines = f.readlines()

        # Copy the startup script to the dir
        local_sbsprj_scripts_dir = os.path.join(self.local_sbsprj_dir, "scripts")
        local_sbsprj_script_path = os.path.join(local_sbsprj_scripts_dir, "__startup__.py")
        plugin = juniper.plugins.PluginManager().find_plugin("designer")
        designer_startup_script_path = os.path.join(plugin.root, "Source\\Bootstrap\\__bootstrap__.py")
        if(not os.path.isdir(os.path.join(local_sbsprj_scripts_dir))):
            os.makedirs(local_sbsprj_scripts_dir)
        with open(local_sbsprj_script_path, "w") as f:
            with open(designer_startup_script_path, "r") as script:
                f.writelines(script.readlines())

        # Inline replace the data to point to the current juniper location
        # Note: This will need to be updated whenever Juniper is moved
        for i in range(len(shelf_lines)):
            line = shelf_lines[i]
            if("$(PLUGINS_DIR)" in line):
                shelf_lines[i] = line.replace("$(PLUGINS_DIR)", local_sbsprj_scripts_dir)
            if("$(PROJECT_NAME)" in line):
                shelf_lines[i] = line.replace("$(PROJECT_NAME)", "Juniper")

        with open(self.local_sbsprj_path, "w+") as f:
            f.writelines(shelf_lines)

        juniper_designer.add_sbsprj(self.local_sbsprj_path)

    @property
    def sbsprj_template_path(self):
        """
        :return <str:path> The path to the base config file used as a template substance project
        """
        return os.path.join(juniper.paths.root(), "Config\\Programs\\Designer\\project.sbsprj.template")

    @property
    def local_sbsprj_dir(self):
        """
        :return <str:dir> The directory containing all generated data for the substance integration
        """
        return os.path.join(juniper.paths.root(), "Cached\\BoilerPlate\\Designer\\JuniperShelf")

    @property
    def local_sbsprj_path(self):
        """
        :return <str:path> The path to the generated substance project for Juniper
        """
        return os.path.join(self.local_sbsprj_dir, "juniper" + ".sbsprj")


DesignerInstaller()
