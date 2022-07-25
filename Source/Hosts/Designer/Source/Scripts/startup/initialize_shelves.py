"""
:type script
:callbacks [startup]
:desc Initializes all available Juniper shelves for Designer
"""
import os

import juniper
import juniper.paths
import juniper.engine.types.plugin

import sd.juniper


for plugin in juniper.engine.types.plugin.PluginManager():
    if(plugin.enabled):
        shelf_dir = os.path.join(plugin.root, "Resources\\Shelves\\Designer")
        if(os.path.isdir(shelf_dir)):
            sd.juniper.add_shelf(plugin.name, shelf_dir)
            juniper.log.info(f"Registered shelf for plugin: {plugin.name}")
