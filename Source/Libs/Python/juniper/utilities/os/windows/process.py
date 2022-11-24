"""
Windows utility functions for interacting with processes
"""
import ctypes


def get_foreground_hwnd():
    """
    Gets the currently selected foreground HWND (active window on the users machine)
    :return <int:hwnd> The current foreground hwnd
    """
    foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
    foreground_hwnd_parent = ctypes.windll.user32.GetParent(foreground_hwnd)
    while(1):
        if(foreground_hwnd_parent):
            foreground_hwnd = foreground_hwnd_parent
            foreground_hwnd_parent = ctypes.windll.user32.GetParent(foreground_hwnd)
        else:
            break
    return foreground_hwnd


def get_process_id(hwnd):
    """
    Gets the id of the parent process for an HWND
    :param <int:hwnd> The HWND to get the process id for
    :return <int:pid> The process ID for the hwnd
    """
    lpdw_process_id = ctypes.c_ulong()
    c_hwnd = ctypes.wintypes.HWND(hwnd)
    ctypes.windll.user32.GetWindowThreadProcessId(c_hwnd, ctypes.byref(lpdw_process_id))
    return lpdw_process_id.value
