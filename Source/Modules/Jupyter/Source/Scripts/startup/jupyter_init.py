"""
:type script
:callbacks [startup]
:desc Initializes Jupyter
"""
import juniper.engine

import json
import os


kernel_display_name = "Jupyter IPyKernel"
kernel_name = "juniper_ipykernel"
python_exe_path = os.path.join(juniper.engine.JuniperEngine().workspace_root, "Binaries\\Python\\3.7\\python.exe")
kernel_dir = os.path.join(os.environ['APPDATA'], "Jupyter\\kernels")

os.makedirs(kernel_dir, exist_ok=True)

kernel_json = {
    "argv": [python_exe_path, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
    "display_name": kernel_name,
    "language": "python"
}

with open(os.path.join(kernel_dir, "juniper_kernel.json"), "w") as f:
    json.dump(kernel_json, f, indent=4, sort_keys=True)

print(f"Kernel {kernel_name} created in {kernel_dir}")
