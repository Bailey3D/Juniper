import clr


clr.AddReference("Autodesk.Max")
from Autodesk.Max import GlobalInterface


def GetCOREInterface():
    """
    Gets the CORE interface from the SDK/C#
    :return <COREInterface:core_interface> The COREInterface as retrieved from c# libs
    """
    return GetGlobalInterface().UtilGetCOREInterface


def GetGlobalInterface():
    """
    Gets the global interface from the SDK/C#
    :return <GlobalInterface:global_interface> Global interface as retrieved from the c# libs
    """
    return GlobalInterface.Instance


def GetActiveViewExp():
    """
    Gets the active viewport
    :return <ViewExp:view_exp)
    """
    return GetCOREInterface().ActiveViewExp


def GetTime():
    """
    Gets the current Max time
    :return <int:time> Current Time
    """
    return GetCOREInterface().Time
