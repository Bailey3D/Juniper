"""
:type tool
:desc Generates / updates the vscode workspace found under `//juniper/.vscode/Juniper.code-workspace`
"""
import juniper.framework.programs.vscode


juniper.framework.programs.vscode.generate_code_workspace()
