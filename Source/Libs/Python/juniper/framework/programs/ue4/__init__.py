import os
import socket

import juniper
import juniper.utilities.json as json_utils
import juniper.framework.command_server


def unreal_project_path():
    """Returns the path to the current unreal project .uproject\n
    :return <str:path> Path to the .uproject\n
    """
    return json_utils.get_property(
        os.path.join(juniper.paths.root(), "Cached\\UserConfig\\user_settings.json"),
        "unreal_project_path"
    )


def unreal_project_dir():
    """Returns the path to the current unreal project directory\n
    :return <str:dir> Directory path to the unreal project (the directory containing the .uproject file)\n
    """
    return os.path.dirname(unreal_project_path()).lower()


def listen_port():
    """Returns the server port that the unreal listen server is hosted on\n
    :return <int:port> The port to the unreal listen server\n
    """
    return json_utils.get_property(juniper.paths.get_config("program.json", program="ue4"), "listen_port")


def launch_unreal_project():
    """Launch the current unreal project standalone"""
    os.system("start " + unreal_project_path())


def is_open():
    """Check if the program is open by testing if the listen server is hosted
    :return <bool:open> True if the project is open, false if not
    """
    return not juniper.framework.command_server.is_free(listen_port())


def send_command(command):
    """Takes a python string command and sends it as a request to the listen server\n
    :param <str:command> Python command to run\n
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
