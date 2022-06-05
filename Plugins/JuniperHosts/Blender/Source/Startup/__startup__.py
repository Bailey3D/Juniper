"""
Base startup for Blender integration
"""

# Attaching to `bpy` is disabled atm - because the `__path__` property seems to be wiped on startup?

'''import bpy
import os

import juniper.plugins


# Add the Juniper Bpy libraries as a path to the inbuild `bpy` package
bpy_plugin = juniper.plugins.PluginManager().find_plugin("blender")
if(hasattr(bpy, "__path__")):
    bpy.__path__.append(os.path.join(bpy_plugin.root, "Source\\Libs\\Python\\bpy"))
else:
    bpy.__path__ = [os.path.join(bpy_plugin.root, "Source\\Libs\\Python\\bpy")]'''
