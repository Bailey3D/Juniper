"""
:script
:type startup
:desc Runs all startup files in the startup folder hierarchies
"""
from importlib.machinery import SourceFileLoader
import os


class Startup(object):
    def __init__(self):
        bootstrap = self.juniper_bootstrap_module
        bootstrap.startup(__program_context__)

    @property
    def juniper_bootstrap_module(self):
        bootstrap_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..\\..\\Source\\Libs\\Python\\juniper\\bootstrap.py"
        ))
        return SourceFileLoader("juniper_bootstrap", bootstrap_path).load_module()


Startup()
