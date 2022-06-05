"""
Base startup for 3DS Max integration
"""
import pymxs
import os

import juniper.plugins


# Add the Juniper 3DS Max libraries as a path to the inbuild `pymxs` package
pymxs_plugin = juniper.plugins.PluginManager().find_plugin("max")
pymxs.__path__.append(os.path.join(pymxs_plugin.root, "Source\\Libs\\Python\\pymxs"))
