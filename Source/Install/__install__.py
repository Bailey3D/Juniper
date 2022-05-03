"""
:script
:type install
:desc Runs all tools initialization files in the install folders
"""
import os
from importlib.machinery import SourceFileLoader


class Install(object):
    def __init__(self):
        self.file = __file__

        bootstrap = self.juniper_bootstrap_module
        bootstrap.install()

    @property
    def juniper_bootstrap_module(self):
        bootstrap_path = os.path.abspath(os.path.join(
            os.path.dirname(self.file),
            "..\\..\\Source\\Libs\\Python\\juniper_bootstrap.py"
        ))
        return SourceFileLoader("juniper_bootstrap", bootstrap_path).load_module()


Install()
