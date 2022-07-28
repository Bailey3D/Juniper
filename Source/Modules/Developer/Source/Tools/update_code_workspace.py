"""
:type tool
:desc Generates / updates the vscode workspace found under `//juniper/.vscode/Juniper.code-workspace`
:category Core
"""
import juniper.developer.programs.vscode


juniper.developer.programs.vscode.generate_code_workspace()
