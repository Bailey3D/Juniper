"""
:type script
:callbacks [startup]
"""
import juniper
import juniper.widgets

import juniper_command_server
from juniper_command_server import command_server


if(juniper.program_context not in ["python"]):
    juniper.widgets.get_application()  # command server uses Qt tick - ensure QApplication is initialized
    port = juniper_command_server.listen_port(juniper.program_context)
    command_server.CommandServer(port)
