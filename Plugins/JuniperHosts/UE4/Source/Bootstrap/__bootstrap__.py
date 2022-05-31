import json
import os
import sys


juniper_config = os.path.join(os.getenv("APPDATA"), "juniper\\config.json")
if(os.path.isfile(juniper_config)):
    with open(juniper_config, "r") as f:
        json_data = json.load(f)
        if("path" in json_data and os.path.isdir(json_data["path"])):
            startup_path = os.path.join(json_data["path"], "Source\\Startup\\__startup__.py")
            globals_ = globals()
            globals_["__file__"] = startup_path
            globals_["__package__"] = os.path.dirname(startup_path)
            sys.argv.append("juniper:program_context=ue4")
            with open(startup_path, "r") as f:
                exec(f.read(), globals_)
