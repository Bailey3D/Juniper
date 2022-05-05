import json

import juniper
import juniper.widgets
import juniper.framework.command_server
import juniper.framework.backend.plugin


if(juniper.program_context not in ["python"]):
    juniper.widgets.get_application()  # command server uses Qt tick - ensure QApplication is initialized

    this_plugin = juniper.framework.backend.plugin.PluginManager().find_plugin("juniper_command_server")
    command_server_json = os.path.join(this_plugin.root, "Config\\command_server.json")
    with open(command_server_json, "r") as f:
        json_data = json.load(f)
        if(juniper.program_context in json_data["ports"]):
            juniper.framework.command_server.CommandServer(json_data["ports"][juniper.program_context])
        else:
            juniper.log.error(f"Command Sefer failed to initialize - port not defined for program {juniper.program_context}")
