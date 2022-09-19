import os
import xml.etree.ElementTree

import juniper
import juniper.paths
import juniper.utilities.xml as xml_utils


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


def add_shelf(shelf_name, shelf_root):
    """
    Adds a named shelf to the current designer project\n
    Note: this adds to the local juniper sbsprj - not the global configs\n
    :param <str:shelf_name> The name of the shelf to add / update\n
    :param <str:shelf_root> The root directory of this shelf\n
    """
    juniper_sbsprj_path = os.path.join(
        juniper.paths.root(),
        "Cached\\Programs\\Designer\\juniper.sbsprj"
    )
    print("Doing an add shelf")
    print(juniper_sbsprj_path)

    xml_sbsprj_tree = xml.etree.ElementTree.parse(juniper_sbsprj_path)
    xml_sbsprj_root = xml_sbsprj_tree.getroot()

    xml_config_watchedpaths = xml_sbsprj_root.find("./preferences/library/watchedpaths")
    xml_config_watchedpaths_size = xml_sbsprj_root.find("./preferences/library/watchedpaths/size")
    num_watched_shelves = int(xml_config_watchedpaths_size.text)

    # Create new data
    new_num_watched_shelves = num_watched_shelves
    xml_target_root_node = None

    # Search for already existing shelf w/ this name
    for i in xml_config_watchedpaths:
        if(i.tag.startswith("_")):  # Entries are "_" and then an index (Ie, "_5")
            id_elem = i.find("id")
            if(id_elem is not None and shelf_name == id_elem.text):
                xml_target_root_node = i
                break

    # If no shelf w/ this name exists - we should create a new one
    if(not xml_target_root_node):
        new_num_watched_shelves += 1
        xml_target_root_node = xml.etree.ElementTree.SubElement(xml_config_watchedpaths, f"_{new_num_watched_shelves}")

    # Get / create keys in the new node
    xelem_url = xml_utils.get_or_create_sub_element(xml_target_root_node, "url")
    xelem_id = xml_utils.get_or_create_sub_element(xml_target_root_node, "id")
    xelem_isrecursive = xml_utils.get_or_create_sub_element(xml_target_root_node, "isrecursive")
    xelem_isenabled = xml_utils.get_or_create_sub_element(xml_target_root_node, "isenabled")

    # Set data
    xml_target_root_node.set("prefix", "_")
    xelem_url.text = "file:///" + shelf_root.replace("\\", "/")
    xelem_id.text = shelf_name
    xelem_isrecursive.text = "true"
    xelem_isenabled.text = "true"
    xml_config_watchedpaths_size.text = str(new_num_watched_shelves)

    with open(juniper_sbsprj_path, "w+") as f:
        f.write(xml.etree.ElementTree.tostring(xml_sbsprj_root, encoding="unicode", method="xml"))
