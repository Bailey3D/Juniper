"""
:type tool
:desc This is a template tool found in the `juniper_plugin_template` plugin.
"""
#  This is a template tool. It will be registered as a Script on Juniper startup.
#  The tool can be ran like a macro with the following logic:
#
#  ```
#  import juniper.types.framework.script as script
#  script.ScriptManager().run("template_tool")  # The name of the tool (the filename minus the file type)
#  ```
#
#  Note: Tools should have unique names in order to avoid conflicts.
#        if multiple tools with duplicate names are found, the first instance will be ran.
#
print("Hello World!")
