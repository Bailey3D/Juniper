"""
Base startup for Unreal integration
"""
import unreal
import os

import juniper.plugins


# Add the Juniper Unreal libraries as a path to the inbuild `unreal` package
unreal_plugin = juniper.plugins.PluginManager().find_plugin("unreal")
if(hasattr(unreal, "__path__")):
    unreal.__path__.append(os.path.join(unreal_plugin.root, "Source\\Libs\\Python\\unreal"))
else:
    unreal.__path__ = [os.path.join(unreal_plugin.root, "Source\\Libs\\Python\\unreal")]
