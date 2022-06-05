"""
Base startup for Substance Designer integration
"""
import sd
import os

import juniper.plugins


# Add the Juniper Designer libraries as a path to the inbuild `sd` package
sd_plugin = juniper.plugins.PluginManager().find_plugin("designer")
sd.__path__.append(os.path.join(sd_plugin.root, "Source\\Libs\\Python\\sd"))
