import os
import shutil

import juniper.paths


def copy_startup():
    """copy the "lib/install/juniper.py" to the users "documents/allegorithmic/substance painter/python/startup" """
    shutil.copyfile(
        os.path.join(juniper.paths.root(), "Source\\Startup\\__startup__.painter.py"),
        os.path.join(juniper.paths.documents(), "Allegorithmic\\Substance Painter\\python", "startup\\__juniper_startup__.py")
    )

copy_startup()
