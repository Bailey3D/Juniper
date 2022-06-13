"""
:type tool
:desc Generates / updates the vscode workspace found under `//juniper/.vscode/Juniper.code-workspace`
"""
import juniper_developer.programs.vscode


juniper_developer.programs.vscode.generate_code_workspace()
