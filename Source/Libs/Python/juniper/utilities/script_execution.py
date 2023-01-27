"""
Utility functions for executing various script/tool files
"""
import os
from importlib.machinery import SourceFileLoader

import juniper.engine.paths
import juniper.utilities.json as json_utils


def run_file(file_path, plugin=None):
    """
    Run a tool, this can be from a direct script or a .toolptr filepath
    :param <str:file_path> Path to the script or toolptr to run
    """
    # juniper relative path -> absolute path
    if(not os.path.isfile(file_path)):
        file_path = os.path.join(juniper.engine.paths.root(), file_path)

    elif(file_path.endswith(".ms")):
        import pymxs
        with open(file_path, "r") as f:
            file_lines = f.read()
            pymxs.runtime.execute(file_lines)

    else:
        globals_ = globals()

        if(file_path.endswith(".toolptr")):
            file_path = json_utils.get_property(file_path, "path")
            if(plugin):
                file_path = os.path.join(juniper.engine.paths.get_module_root(plugin))
            else:
                file_path = os.path.join(juniper.engine.paths.root(), file_path)

        if(os.path.isfile(file_path)):
            import juniper_globals
            globals_["__file__"] = file_path
            globals_["__package__"] = os.path.dirname(file_path)
            globals_["__name__"] = "__main__"
            juniper_globals.set("__juniper_exec_file_path__", file_path)
            exec(open(file_path).read(), globals_)


def load_source(module_name, module_path):
    """
    Wrapper for the old 'imp.load_source' method using new method
    :return <Module:module> The loaded module
    """
    return SourceFileLoader(module_name, module_path).load_module()
