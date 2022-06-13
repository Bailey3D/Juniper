"""
:type startup
:desc Runs all startup files in the startup folder hierarchies
"""
from importlib.machinery import SourceFileLoader
import os
import sys


class Startup(object):
    def __init__(self):
        bootstrap = self.juniper_bootstrap_module
        bootstrap.startup(self.program_context)

    @property
    def program_context(self):
        for i in sys.argv:
            if(i.startswith("juniper:program_context=")):
                return i.split("=")[1].lower()
        return "python"

    @property
    def juniper_bootstrap_module(self):
        bootstrap_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..\\..\\Source\\Libs\\Python\\juniper\\bootstrap.py"
        ))
        return SourceFileLoader("juniper_bootstrap", bootstrap_path).load_module()


Startup()
