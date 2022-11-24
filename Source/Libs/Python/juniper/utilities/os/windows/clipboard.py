"""
Utility functions for interacting with the windows clipboard
"""
import ctypes


kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32


def get_clipboard_text():
    """
    Gets the current text in the users clipboard
    :return <str:text> The current clipboard text - None if no text is in the clipboard (Ie, images, or nothing)
    """
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    user32.GetClipboardData.restype = ctypes.c_void_p

    try:
        CF_TEXT = 1
        user32.OpenClipboard(0)
        if user32.IsClipboardFormatAvailable(CF_TEXT):
            data = user32.GetClipboardData(CF_TEXT)
            data_locked = kernel32.GlobalLock(data)
            text = ctypes.c_char_p(data_locked)
            value = text.value
            kernel32.GlobalUnlock(data_locked)
            value = value.decode("utf-8")
            return value
    finally:
        user32.CloseClipboard()
    return None


def copy_to_clipboard(string):
    import subprocess
    subprocess.run('clip', universal_newlines=True, input=string)
