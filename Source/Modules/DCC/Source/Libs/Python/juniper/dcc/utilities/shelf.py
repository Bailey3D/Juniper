import os
import xml.etree.ElementTree

import juniper
import juniper.engine.decorators
import juniper.engine.paths
import juniper.utilities.xml as xml_utils


@juniper.engine.decorators.virtual_method
def add_shelf(shelf_name, shelf_root):
    """
    Adds a shelf to the current host application
    :param <str:shelf_name> The name of the shelf to add
    :param <str:shelf_root> The root directory of the shelf to add
    """
    raise NotImplementedError


@add_shelf.override("designer")
def add_shelf(shelf_name, shelf_root):
    juniper_sbsprj_path = os.path.join(
        juniper.engine.paths.root(),
        "Cached\\Programs\\Designer\\juniper.sbsprj"
    )

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


@add_shelf.override("painter")
def add_shelf(shelf_name, shelf_root):
    import substance_painter.resource
    substance_painter.resource.Shelves.add(shelf_name, shelf_root)

    # Substance Painter 2021 added in support for transient shelves
    # meaning we don't have to add anything to the registry
    #
    # Below is the old method of adding - which required writing to registry
    # ..

    '''painter_reg_name = "Software\\Allegorithmic\\Substance Painter\\Shelf\\pathInfos"

    shelf_name = shelf_name.lower()
    shelf_path = shelf_path.replace("\\", "/")
    shelf_path = shelf_path if (shelf_path[-1] != "/") else shelf_path[0:-1]

    # load the key "reg_name" and build the shelf registry path
    # Note: Is this still under the same key since the switch to Adobe accounts?
    painter_reg_name = "Software\\Allegorithmic\\Substance Painter\\Shelf\\pathInfos"

    #
    reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)

    key = winreg.OpenKey(reg_connection, painter_reg_name, winreg.KEY_READ)
    subkey_count = winreg.QueryInfoKey(key)[0]

    shelf_number = 0
    already_exists = False

    for x in range(subkey_count):
        subkey_name = winreg.EnumKey(key, x)

        target_key = winreg.OpenKey(key, subkey_name, 0, winreg.KEY_ALL_ACCESS)
        target_key_name = winreg.QueryValueEx(target_key, "name")[0]

        # if we find a key with the target name - update the path
        if(target_key_name == shelf_name):
            already_exists = True
            winreg.SetValueEx(target_key, "disabled", 0, winreg.REG_SZ, "true")
            winreg.SetValueEx(target_key, "name", 0, winreg.REG_SZ, shelf_name)
            winreg.SetValueEx(target_key, "path", 0, winreg.REG_SZ, shelf_path)

        target_key.Close()

        if(int(subkey_name) > shelf_number):
            shelf_number = int(subkey_name)

    shelf_number += 1

    if(not already_exists):
        new_key = winreg.CreateKey(key, str(shelf_number))
        winreg.SetValueEx(new_key, "disabled", 0, winreg.REG_SZ, "true")
        winreg.SetValueEx(new_key, "name", 0, winreg.REG_SZ, shelf_name)
        winreg.SetValueEx(new_key, "path", 0, winreg.REG_SZ, shelf_path)

        new_key.Close()
        key.Close()

    # increase shelf count if needed
    key = winreg.OpenKey(reg_connection, painter_reg_name, 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, "size", 0, winreg.REG_DWORD, winreg.QueryInfoKey(key)[0])
    key.Close()'''
