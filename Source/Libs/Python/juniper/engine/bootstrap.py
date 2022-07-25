"""
Standalone module used to bootstrap juniper from within different host contexts
This file should not rely on any external packages/modules - only vanilla Python ones
"""
import functools
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

        self.get_engine_class()

    @property
    @functools.lru_cache()
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
        juniper_config = os.path.join(os.getenv("APPDATA"), "juniper\\config.json")
        with open(juniper_config, "r") as f:
            return json.load(f)["path"]
        return None

    @property
    @functools.lru_cache()
    def get_engine_class(self):
        """
        :return <JuniperEngine:class> The target Juniper Engine class - respective of overrides
        """
        output = None

        if(self.program_context != "python"):
            engine_override_script = os.path.join(
                self.workspace_root,
                "Source\\Hosts",
                self.program_context,
                "Source\\__plugin__.py"
            )
            if(os.path.isfile(engine_override_script)):
                sys.path.insert(0, os.path.join(self.workspace_root, "Source\\Libs\\Python"))
                host_override_module = SourceFileLoader(
                    "juniper_engine_override",
                    engine_override_script
                ).load_module("juniper_engine_override")
                host_override_module
                output = eval(f"host_override_module.{self.program_context.capitalize()}")

        if(not output):

            engine_script = os.path.join(
                self.workspace_root,
                "Source\\Libs\\python\\juniper\\engine\\__init__.py"
            )

            engine_module = SourceFileLoader(
                "juniper_engine",
                engine_script
            ).load_module("juniper_engine")

            output = engine_module.JuniperEngine

        return output
