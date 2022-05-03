"""
Heper functions for VSCode
"""
import json
import os
from collections import OrderedDict

import juniper.framework.backend.module
import juniper.paths


def update_code_workspace():
    """
    Updates the juniper.code-workspace file sorted in the .vscode folder in the root.
    Reinitializes to include all currently used modules.
    """
    workspace_path = os.path.join(juniper.paths.root(), ".vscode\\juniper.code-workspace")

    json_data = OrderedDict()
    json_data["folders"] = []

    json_data["folders"].append({
        "name": "Juniper",
        "path": "..\\"
    })

    for i in juniper.framework.backend.module.ModuleManager:
        if(i.name is not "juniper"):
            json_data["folders"].append({
                "name": os.path.basename(i.module_root),
                "path": f"..\\modules\\{os.path.basename(i.module_root)}"
            })

    with open(workspace_path, "w") as f:
        json.dump(json_data, f, indent=4)
