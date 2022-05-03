"""
Library containing functions for Juniper startup
"""
import os

import juniper
import juniper.paths
import juniper.framework.backend.module


def run():
    """
    Initialize Juniper by running all startup scripts in order
    """
    modules = set()

    base_module = juniper.framework.backend.module.Module("juniper")
    modules.add(base_module)

    # Initialize all modules
    for module_dir in juniper.paths.module_dirs():
        module_name = os.path.basename(module_dir)
        module_ = juniper.framework.backend.module.Module(module_name, module_dir=module_dir)
        modules.add(module_)
        juniper.log.info(f"Initialized Module: {module_name}", silent=True)

    # Initialize internal/external libraries for all modules
    for module in modules:
        module.initialize_libraries()

    # Initialize all macros for the module to ensure they're registered
    for module in modules:
        module.macros
    juniper.log.info("Initialized Juniper Macros", silent=True)

    # Runs all startup scripts for the module
    # None = base `__startup__.py`
    # Other = ordered scripts
    for i in (None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
        for module in modules:
            module.run_startup_scripts(i)
    juniper.log.info("Finished running startup scripts.", silent=True)

    juniper.log.success("Juniper started without errors!", silent=False)
