'''import os
import inspect

import juniper
import juniper.engine


je = juniper.engine.JuniperEngine()
pc = je.program_context

host_root = os.path.join(
    je.workspace_root,
    "Source\\Hosts",
    je.name
)
host_override_path = os.path.join(
    host_root,
    "Source\\Libs\\Python\\overrides.py"
)

print(host_override_path)
print(os.path.isfile(host_override_path))
'''
import juniper
import tools_library.asset_library as a
print(a)