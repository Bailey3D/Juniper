"""
Base startup for Substance Painter integration
"""
import substance_painter
import os

import juniper.plugins


# Add the Juniper Substance Painter libraries as a path to the inbuild `substance_painter` package
painter_plugin = juniper.plugins.PluginManager().find_plugin("painter")
substance_painter.__path__.append(os.path.join(painter_plugin.root, "Source\\Libs\\Python\\substance_painter"))
