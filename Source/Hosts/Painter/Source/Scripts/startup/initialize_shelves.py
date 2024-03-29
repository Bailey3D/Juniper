"""
:type script
:callbacks [startup]
:desc Initializes all available Juniper shelves for Painter
"""
import os

import juniper
import juniper.engine.paths
import juniper.engine.types.plugin

import substance_painter.juniper.shelf


for plugin in juniper.engine.types.plugin.PluginManager():
    if(plugin.enabled):
        shelf_dir = os.path.join(plugin.root, "Resources\\Shelves\\Painter")
        if(os.path.isdir(shelf_dir)):
            substance_painter.juniper.shelf.add_shelf(plugin.name, shelf_dir)
            juniper.log.info(f"Registered shelf for plugin: {plugin.name}")
