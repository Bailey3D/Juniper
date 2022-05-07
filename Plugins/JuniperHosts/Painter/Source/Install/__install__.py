import os
import shutil

import juniper.framework.backend.plugin
import juniper.paths


def copy_startup():
    """copy the "lib/install/juniper.py" to the users "documents/allegorithmic/substance painter/python/startup" """
    plugin = juniper.framework.backend.plugin.PluginManager().find_plugin("painter")
    shutil.copyfile(
        os.path.join(plugin.root, "Source\\Bootstrap\\__bootstrap__.py"),
        os.path.join(juniper.paths.documents(), "Allegorithmic\\Substance Painter\\python", "startup\\__juniper_startup__.py")
    )


copy_startup()
