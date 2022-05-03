import contextlib
import functools
import os
from qtpy import QtWidgets, QtCore
import select
import socket
import textwrap

import juniper
import juniper.decorators
import juniper.framework.types.singleton
import juniper.paths
import juniper.utilities.json as json_utils
import juniper_globals


def listen_port(program_name):
    """
    Returns the port that the given program listen server is hosted on
    :param <str:program_name> The name of the program to get the port for
    :return <int:port> Id of the port - None if it is not set in the config
    """
    config_path = juniper.paths.get_config("program.json", program=program_name)
    if(os.path.isfile(config_path)):
        return json_utils.get_property(config_path, "listen_port")
    return None


def is_free(port):
    """
    Returns whether a port is free
    :param <int:port> Port index
    :return <bool:free> True if free, false if not
    """
    if(port is not None):
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        loc = ("localhost", port)
        output = test_socket.connect_ex(loc) != 0
        test_socket.close()
        return output
    return False


def send_command(command, program_name):
    """
    Takes a python string command and sends it as a request to the listen server
    :param <str:command> Python command to send
    :return <bool:success> True if the command was sent - else False
    """
    port = listen_port(program_name)
    if(not is_free(port)):
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
    if(not is_free(port)):
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


class CommandServer(metaclass=juniper.framework.types.singleton.Singleton):
    def __init__(self):
        """
        A non-blocking listen server object
        :param <int:port> The port to bind this listen server to
        """
        if(not self.port):
            juniper.log.error(f"Command Server Initialization Failed: No port set for the program {juniper.program_context}", traceback=False)
            self.initialized = False
            return
        elif(not is_free(self.port)):
            juniper.log.error(f"Command Server Initialization Failed: Another program is using the port {self.port}", traceback=False)
            self.initialized = False
            return

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("localhost", self.port))
        self.server_socket.listen(0)
        self.server_socket.setblocking(0)
        self.read_list = [self.server_socket]

        try:
            # Temporarily stops the "ConnectionRefusedError" from displaying in the logs
            # sending an empty command is only a workaround to stop blocking on the listen server
            # and if the connection fails then we get around the initial blocking anyway
            # we must send an initial command else the server will block the program until the first connection
            null = open(os.devnull, "wb")
            with contextlib.redirect_stderr(null):
                init_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                init_client.connect(("localhost", self.port))
                init_client.send(str("").encode("utf-8"))
                init_client.setblocking(0)
                init_client.close()
                juniper_globals.set("command_server", self)
                self.initialized = True
        except Exception:
            self.initialized = False

        if(self.initialized):
            juniper.log.info(f"Command server for {juniper.program_context} was bound to port {self.port}", silent=False)
        else:
            juniper.log.warning("Unable to initialize listen server for the current program.", traceback=False)

        self.bind_tick()

    def close(self):
        """Close the listen server"""
        self.server_socket.close()

    # ----------------------------------------------------------------

    @juniper.decorators.virtual_method
    def bind_tick(self):
        """
        Bind the tick command to update with the host application
        """
        if(QtWidgets.QApplication.instance()):
            if(listen_port):
                timer_ = QtCore.QTimer()
                timer_.timeout.connect(self.tick)
                timer_.start(20)
                self.tick_timer = timer_

    @bind_tick.override("ue4")
    def _bind_tick(self):
        import unreal

        def slate_tick(delta_seconds):
            """Function bound to unreal's slate tick"""
            self.tick()

        def engine_shutdown():
            """Called when unreal shuts down"""
            unreal.unregister_slate_post_tick_callback(slate_tick_handle)
            unreal.unregister_python_shutdown_callback(engine_shutdown_handle)

        slate_tick_handle = unreal.register_slate_post_tick_callback(slate_tick)
        engine_shutdown_handle = unreal.register_python_shutdown_callback(engine_shutdown)

    @bind_tick.override("python")
    def _bind_tick(self):
        # Do not tick the command server if running a standalone python.
        pass

    def tick(self):
        """Update the listen server and check for calls"""
        if(self.initialized):
            readable, writable, errored = select.select(self.read_list, [], [])
            for s in readable:
                if(s is self.server_socket):
                    client_socket, address = self.server_socket.accept()
                    self.read_list.append(client_socket)
                else:
                    # NOTE: We may need to up the size if we end up sending large scripts to run
                    data = (s.recv(1024)).decode("utf-8")
                    if(data):
                        try:
                            exec(compile(data, "-", "exec"))
                        except Exception:
                            pass

    # ----------------------------------------------------------------

    @property
    @functools.lru_cache()
    def port(self):
        program_config_path = juniper.paths.get_config("program.json", program=juniper.program_context)
        return json_utils.get_property(program_config_path, "listen_port") or None