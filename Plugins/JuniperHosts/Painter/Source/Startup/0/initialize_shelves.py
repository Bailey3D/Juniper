"""
:type startup
:desc Initializes all available Juniper shelves for Painter
"""
import os

import juniper
import juniper.paths
import juniper.plugins

import juniper_painter.shelf


for plugin in juniper.plugins.PluginManager():
    if(plugin.enabled):
        shelf_dir = os.path.join(plugin.root, "Resources\\Shelves\\Painter")
        if(os.path.isdir(shelf_dir)):
            juniper_painter.shelf.add_shelf(plugin.name, shelf_dir)
            juniper.log.info(f"Registered shelf for plugin: {plugin.name}")
