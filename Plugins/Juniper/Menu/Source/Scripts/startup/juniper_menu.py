"""
:type script
:callbacks [startup]
:desc Startup script used to initialize a tools menu in the current host program
:todo~ Add in support for Houdini / other hosts
:supported_hosts [max, unreal, blender, designer, painter, juniper_hub]
"""
import juniper
import juniper.types.framework.script
import juniper_menu


this_script = juniper.types.framework.script.Script(__file__)
if(juniper.program_context in this_script.supported_hosts):
    tm = juniper_menu.JuniperMenu()
