"""
Module used to cache various global type data throughout the Juniper instance

Ie, instances of tool windows use 'inspect.getfile' which fails when created throgh
'juniper.utilities.script_execution.run_tool' due to the standalone tool module
being seen as an in-built class. So we must cache the *actual* path to be retrieved later on in the classes creation
"""


class __GlobalsManager(object):
    __instance__ = None

    def __init__(self):
        self.GLOBALS = {}


if(not __GlobalsManager.__instance__):
    __GlobalsManager.__instance__ = __GlobalsManager()
GlobalsManager = __GlobalsManager.__instance__


def get(key):
    """
    Gets a Juniper global
    :param <str:key> The key to get
    :return <object:value> The value
    """
    if(key in GlobalsManager.GLOBALS):
        return GlobalsManager.GLOBALS[key]
    return None


def set(key, value):
    """
    Sets a Juniper global
    :param <str:key> The name of the key to set
    :param <object:value> The vaule to set
    """
    GlobalsManager.GLOBALS[key] = value
