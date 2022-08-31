"""
Module containing base logic for abstract menu creation.
This module is also responsible for creating menus to launch all available Juniper tools in a range of host applications.
"""
import juniper.engine.types.module


class Menu(juniper.engine.types.module.Module):
    def on_startup(self):
        pass