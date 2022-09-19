"""
Base implementation for Juniper support in Substance Designer
"""
import os
import xml.etree.ElementTree

import juniper.engine


class Designer(juniper.engine.JuniperEngine):
    def on_pre_startup(self):
        """
        Add the `sd.juniper` package to the `sd.__path__`
        """
        import sd
        sd.__path__.append(os.path.join(
            self.workspace_root, "Source\\Hosts\\Designer\\Source\\Libs\\Python\\sd"
        ))

    def on_install(self):
        """
        Installs the Juniper bootstrap to Substance Designer
        """
        # 1) Make target project directory
        if(not os.path.isdir(self.local_sbsprj_dir)):
            os.makedirs(self.local_sbsprj_dir)

        # 3) Copy to startup dir
        local_sbsprj_scripts_dir = os.path.join(self.local_sbsprj_dir, "scripts")
        local_sbsprj_script_path = os.path.join(local_sbsprj_scripts_dir, "__startup__.py")
        self.create_bootstrap_file(local_sbsprj_script_path)

        # 2) Read template sbsprj lines
        shelf_lines = []
        with open(self.sbsprj_template_path, "r") as f:
            shelf_lines = f.readlines()

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

        self.add_sbsprj(self.local_sbsprj_path)

    def bootstrap_call_lines(self):
        """
        Substance Designer requires specific methods for startup/shutdown of plugins
        """
        return [
            "def initializeSDPlugin():",
            "    Bootstrap()",
            "def uninitializeSDPlugin():",
            "    pass"
        ]

    # ----------------------------------------------------------------

    @property
    def sbsprj_template_path(self):
        """
        :return <str:path> The path to the base config file used as a template substance project
        """
        return os.path.join(self.workspace_root, "Source\\Hosts\\Designer\\Config\\project.sbsprj.template")

    @property
    def local_sbsprj_dir(self):
        """
        :return <str:dir> The directory containing all generated data for the substance integration
        """
        return os.path.join(self.workspace_root, "Cached\\Programs\\Designer")

    @property
    def local_sbsprj_path(self):
        """
        :return <str:path> The path to the generated substance project for Juniper
        """
        return os.path.join(self.local_sbsprj_dir, "juniper" + ".sbsprj")

    def add_sbsprj(self, sbsprj_path):
        """
        Adds a new sbsprj to the designer library\n
        :param <str:sbsprj_path> Path to the sbsprj to add\n
        """
        if(os.path.isfile(sbsprj_path)):
            sbsprj_set = False
            designer_project_config_path = os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Adobe\\Adobe Substance 3D Designer\\default_configuration.sbscfg"
            )

            if(not os.path.isfile(designer_project_config_path)):
                designer_project_config_path = os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    "Allegorithmic\\Substance Designer\\default_configuration.sbscfg"
                )

            xml_config_tree = xml.etree.ElementTree.parse(designer_project_config_path)
            xml_config_root = xml_config_tree.getroot()

            xml_config_plugins_size = xml_config_root.find("./projects/projectfiles/size")
            xml_config_projects = xml_config_root.findall(".//*path")
            num_projects = int(xml_config_plugins_size.text)

            for xml_config_project in list(xml_config_projects):
                if(sbsprj_path.replace("\\", "/") in xml_config_project.text):
                    sbsprj_set = True

            if(not sbsprj_set):
                xml_config_plugins_size.text = str(num_projects + 1)
                xml_config_projects_root = xml_config_root.find("./projects/projectfiles")
                xml_config_project = xml.etree.ElementTree.SubElement(xml_config_projects_root, "_" + str(num_projects + 1))
                xml_config_project.set("prefix", "_")
                xml_config_project_path = xml.etree.ElementTree.SubElement(xml_config_project, "path")
                xml_config_project_path.text = sbsprj_path.replace("\\", "/")

            with open(designer_project_config_path, "w+") as f:
                f.write(xml.etree.ElementTree.tostring(xml_config_root, encoding="unicode", method="xml"))

    def get_main_window(self):
        import sd.juniper.instance
        return sd.juniper.instance.get_main_qt_window()