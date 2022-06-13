"""
:type install
:desc Generates / updates the vscode workspace found under `//juniper/.vscode/Juniper.code-workspace`
"""
import juniper.plugins
import juniper.types.framework.script


juniper.types.framework.script.ScriptManager().find(
    "update_code_workspace",
    "juniper_developer"
).run()
