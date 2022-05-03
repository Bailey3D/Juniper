import os
import socket
import xml.etree.ElementTree

import juniper
import juniper.paths
from juniper.utilities import json as json_utils
import juniper.framework.command_server


def listen_port():
    """Returns the port that the designer listen server is hosted on\n
    :return <int:port> Id of the port\n
    """
    return json_utils.get_property(juniper.paths.get_config("program.json", program="designer"), "listen_port")


def send_command(command):
    """Takes a python string command and sends it as a request to the listen server
    :param <str:command> Python command to send
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", listen_port()))
    client.send(str(command).encode("utf-8"))
    client.close()


def send_commands(*args):
    """"""
    commands = ""
    for i in args:
        commands += i + "\n"
    send_command(commands)


def is_open():
    """Check if the program is open by testing if the listen server is hosted\n
    :return <bool:open> True if open, false if not\n
    """
    return not juniper.framework.command_server.is_free(listen_port())


def add_sbsprj(sbsprj_path):
    """Adds a new sbsprj to the designer library
    :param <str:sbsprj_path> Path to the sbsprj to add
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


def create_shelf(shelf_name, shelf_root, display_name=None):
    """Creates a Substance Designer shelf and adds it to the program search paths
    :param <str:shelf_name> Code name of the shelf to add
    :param <str:shelf_root> Real path to the root of the shelf
    :param [<str:display_name>] Display name of the shelf - defaults to the shelf name if left as default
    """
    shelf_root = shelf_root.replace("\\", "/")
    if(not display_name):
        display_name = shelf_name

    template_shelf_sbsprj_path = juniper.paths.get_config("shelf.sbsprj.template", program="designer")
    shelf_local_sbsprj_dir = os.path.join(juniper.paths.root(), "config\\designer\\local_shelves")
    shelf_local_sbsprj_path = os.path.join(shelf_local_sbsprj_dir, shelf_name + ".sbsprj")

    already_exists = os.path.isfile(shelf_local_sbsprj_path)

    if(os.path.isfile(template_shelf_sbsprj_path)):
        if(not os.path.isdir(shelf_local_sbsprj_dir)):
            os.makedirs(shelf_local_sbsprj_dir)

        shelf_lines = []
        with open(template_shelf_sbsprj_path, "r") as f:
            shelf_lines = f.readlines()

        for i in range(len(shelf_lines)):
            line = shelf_lines[i]
            if("$(SHELF_PATH)" in line):
                shelf_lines[i] = line.replace(
                    "$(SHELF_PATH)",
                    shelf_root
                )
            elif("$(SHELF_NAME)" in line):
                shelf_lines[i] = line.replace(
                    "$(SHELF_NAME)",
                    display_name
                )

        with open(shelf_local_sbsprj_path, "w+") as f:
            f.writelines(shelf_lines)

    if(not already_exists):
        add_sbsprj(shelf_local_sbsprj_path)
