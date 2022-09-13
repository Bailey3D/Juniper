"""
:type script
:callbacks [startup]
:desc Startup script used to initialize a tools menu in the current host program
:todo~ Add in support for Houdini / other hosts
:supported_hosts [max, unreal, blender, designer, painter, juniper_hub]
"""
import jinterface.menu


tm = jinterface.menu.JuniperMenu()
