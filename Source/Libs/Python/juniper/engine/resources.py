import os

import juniper.engine.paths


def default_icon_path():
    """
    :return <str:path> The path to the `app_default.png` icon
    """
    return os.path.join(
        juniper.engine.paths.root(),
        "Resources\\Icons\\Standard\\app_default.png"
    )
