"""
Standalone module used to bootstrap juniper from within different host contexts
This file should not rely on any external packages/modules - only vanilla Python ones
"""
import functools
import inspect
import json
import os
import sys
from importlib.machinery import SourceFileLoader


class Bootstrap(object):
    def __init__(self):
        # initialize the juniper_globals module
        SourceFileLoader(
            "juniper_globals",
            os.path.join(self.workspace_root, "Source\\Libs\\python\\juniper_globals.py")
        ).load_module("juniper_globals")

        sys.path.insert(0, os.path.join(self.workspace_root, "Source\\Libs\\Python"))

        self.engine_override_class()

    @property
    def program_context(self):
        """
        :return <str:context> The current program context
        """
        for i in sys.argv:
            if(i.startswith("juniper:program_context=")):
                return i.split("=")[1].lower()
        return "python"

    @property
    @functools.lru_cache()
    def workspace_root(self):
        """
        :return <str:dir> The root directory for Juniper
        """
        if("juniper:install=true" in sys.argv):
            return os.path.abspath(os.path.dirname(__file__) + "\\..\\..\\..\\..\\..\\..")
        juniper_config = os.path.join(os.getenv("APPDATA"), "juniper\\config.json")
        with open(juniper_config, "r") as f:
            return json.load(f)["path"]
        return None

    @property
    def engine_base_class(self):
        engine_script = os.path.join(
            self.workspace_root,
            "Source\\Libs\\python\\juniper\\engine\\__init__.py"
        )
        engine_module = SourceFileLoader(
            "juniper_engine",
            engine_script
        ).load_module("juniper_engine")
        return engine_module.JuniperEngine

    @property
    def engine_override_class(self):
        if(self.program_context != "python"):
            engine_override_script = os.path.join(
                self.workspace_root,
                "Source\\Hosts",
                self.program_context,
                "__host__.py"
            )
            if(os.path.isfile(engine_override_script)):
                host_override_module = SourceFileLoader(
                    f"juniper_engine_override_{self.program_context}",
                    engine_override_script
                ).load_module(f"juniper_engine_override_{self.program_context}")
                for _, member_data in inspect.getmembers(host_override_module):
                    if(inspect.isclass(member_data)):
                        if("JuniperEngine" in [str(x.__name__) for x in member_data.__bases__]):
                            return member_data
        return self.engine_base_class
