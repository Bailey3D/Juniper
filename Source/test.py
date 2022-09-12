'''import juniper.widgets
import ctypes
from qtpy import QtWidgets

user32 = ctypes.windll.user32

print(user32.DisableProcessWindowsGhosting())


app = juniper.widgets.get_application()
w = QtWidgets.QWidget()
w.show()

while 1:
        pass
'''
import os
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
