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
