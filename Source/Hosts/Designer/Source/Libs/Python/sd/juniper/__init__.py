import os
import xml.etree.ElementTree

import juniper
import juniper.paths
import juniper.dcc.utilities.shelf


def add_sbsprj(sbsprj_path):
    """
    Adds a new sbsprj to the designer library\n
    :param <str:sbsprj_path> Path to the sbsprj to add\n
    """
    if(os.path.isfile(sbsprj_path)):
        sbsprj_set = False
        designer_project_config_path = os.path.join(
            juniper.paths.local_appdata(),
            "Adobe\\Adobe Substance 3D Designer\\default_configuration.sbscfg"
        )

        if(not os.path.isfile(designer_project_config_path)):
            designer_project_config_path = os.path.join(
                juniper.paths.local_appdata(),
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


add_shelf = juniper.dcc.utilities.shelf.add_shelf
