"""
Windows based utility functions
"""
import ctypes


def disable_window_ghosting():
    """
    Disables the windows ghosting on the current process ("Not Responding" grayed out windows)
    :return <bool:success> True if the call was successful - else False
    """
    try:
        user32 = ctypes.windll.user32
        user32.DisableProcessWindowsGhosting()
        return True
    except Exception:
        return False


def is_admin():
    """
    Gets whether the current user has admin rights
    :return <bool:state> True if the user has admin rights - else False
    """
    return ctypes.windll.shell32.IsUserAnAdmin() != 0
