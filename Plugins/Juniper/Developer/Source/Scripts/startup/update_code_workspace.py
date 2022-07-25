"""
:type script
:callbacks [startup]
:desc Generates / updates the vscode workspace found under `//juniper/.vscode/Juniper.code-workspace`
"""
import juniper.engine


juniper.engine.JuniperEngine().find_tool("update_code_workspace").run()
