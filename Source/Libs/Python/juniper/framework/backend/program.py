"""
Library containing functions for dealing with the current host program

NOTE: These should all be program agnostic
"""
import os

import juniper.paths
import juniper.utilities.script_execution
import juniper.utilities.json as json_utils


def program_context():
    """Gets the current program context (Ie, "designer", "python", "max")\n
    :return <str:context> Program context as set in the startup scripts - defaults to "python"\n
    """
    import juniper_globals
    output = juniper_globals.get("program_context") or "python"
    return output


def program_names():
    """Get a list of all juniper program names\n
    :return <[str]:names> Listy of all program names\n
    """
    output = []
    scripts_dir = os.path.join(juniper.paths.root(), "scripts")
    for i in os.listdir(scripts_dir):
        install_dir = os.path.join(scripts_dir, i, "install")
        if(i != "common" and os.path.isdir(install_dir)):
            output.append(i.lower())
    return output
