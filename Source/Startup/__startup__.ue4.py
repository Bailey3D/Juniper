import json
import os


def path():
    '''Returns the stored juniper root path as stored in the registry'''
    juniper_config = os.path.join(os.getenv("APPDATA"), "juniper\\config.json")
    with open(juniper_config, "r") as f:
        return json.load(f)["path"]


def run_file_(file_path):
    path_ = file_path
    globals_ = globals()
    globals_["__file__"] = path_
    globals_["__package__"] = os.path.dirname(file_path)
    globals_["__program_context__"] = "ue4"
    exec(open(path_).read(), globals_)


run_file_(path() + "\\Source\\Startup\\__startup__.py")
