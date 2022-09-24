import os

import juniper
import juniper.utilities.json as json_utils


def unreal_project_path():
    """Returns the path to the current unreal project .uproject\n
    :return <str:path> Path to the .uproject\n
    """
    return json_utils.get_property(
        os.path.join(juniper.paths.root(), "Cached\\UserConfig\\user_settings.json"),
        "unreal_project_path"
    )


def unreal_project_dir():
    """Returns the path to the current unreal project directory\n
    :return <str:dir> Directory path to the unreal project (the directory containing the .uproject file)\n
    """
    uproject_path = unreal_project_path()
    if(uproject_path and os.path.isfile(uproject_path)):
        return os.path.dirname(unreal_project_path()).lower()
    else:
        return None


def launch_unreal_project():
    """Launch the current unreal project standalone"""
    os.system("start " + unreal_project_path())
