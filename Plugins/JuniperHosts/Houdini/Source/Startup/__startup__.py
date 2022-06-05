"""
Base startup for Houdini integration
"""
import hou
import os

import juniper.plugins


# Add the Juniper Houdini libraries as a path to the inbuild `hou` package
hou_plugin = juniper.plugins.PluginManager().find_plugin("houdini")
hou.__path__.append(os.path.join(hou_plugin.root, "Source\\Libs\\Python\\hou"))
