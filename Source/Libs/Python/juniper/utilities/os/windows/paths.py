"""
Windows file path based utility functions
"""
import os
import ctypes
import ctypes.wintypes


def documents():
    """
    :return <str:dir> Path to the current users documents directory
    """
    CSIDL_PERSONAL = 5
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    return str(buf.value)


def local_appdata():
    """
    :return <str:path> The path to the users Local Appdata directory
    """
    return os.getenv("LOCALAPPDATA")