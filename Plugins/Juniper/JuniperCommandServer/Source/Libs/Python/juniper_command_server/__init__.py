"""
Base module for the Juniper Command Server plugin
"""
import socket
import textwrap

import juniper.plugins
import juniper.framework.programs

import juniper_command_server.command_server


def listen_port(program_name):
    """
    Returns the port that the given program listen server is hosted on
    :param <str:program_name> The name of the program to get the port for
    :return <int:port> Id of the port - None if it is not set in the config
    """
    supported_hosts = juniper.framework.programs.supported_hosts()
    if(program_name in supported_hosts):
        return 9810 + supported_hosts.index(juniper.program_context)
    return None


def send_command(command, program_name):
    """
    Takes a python string command and sends it as a request to the listen server
    :param <str:command> Python command to send
    :return <bool:success> True if the command was sent - else False
    """
    port = listen_port(program_name)
    if(not juniper_command_server.command_server.is_free(port)):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", port))
        client.send(str(command).encode("utf-8"))
        client.close()
        return True
    return False


def run_file(file_path, program_name):
    """
    Runs a file in the given program context
    :param <str:file_path> The absolute path to the file to run
    :param <str:program_name> The name of the program context to run in
    :return <bool:success> True if the command was sent successfully - else False
    """
    port = listen_port(program_name)
    if(not juniper_command_server.command_server.is_free(port)):
        command = textwrap.dedent(f"""
            import juniper.utilities.script_execution
            juniper.utilities.script_execution.run_file("{file_path}")
        """)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", port))
        client.send(str(command).encode("utf-8"))
        client.close()
        return True
    return False
