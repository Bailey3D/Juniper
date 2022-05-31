import juniper
import juniper.paths

import ctypes
import ctypes.wintypes
import os
import sys


def pythonw_path():
    juniper_pythonw_exe_path = os.path.join(juniper.paths.root(), "Binaries\\Python\\Python37\\Pythonw.exe").lower()
    juniper_pythonw_exe_path_upper = juniper_pythonw_exe_path.replace(os.path.dirname(juniper.paths.root()).lower() + "\\", "")
    return juniper_pythonw_exe_path_upper


def find_and_close():
    Psapi = ctypes.WinDLL('Psapi.dll')
    EnumProcesses = Psapi.EnumProcesses
    EnumProcesses.restype = ctypes.wintypes.BOOL
    GetProcessImageFileName = Psapi.GetProcessImageFileNameA
    GetProcessImageFileName.restype = ctypes.wintypes.DWORD

    Kernel32 = ctypes.WinDLL('kernel32.dll')
    OpenProcess = Kernel32.OpenProcess
    OpenProcess.restype = ctypes.wintypes.HANDLE
    TerminateProcess = Kernel32.TerminateProcess
    TerminateProcess.restype = ctypes.wintypes.BOOL
    CloseHandle = Kernel32.CloseHandle

    MAX_PATH = 260
    PROCESS_TERMINATE = 0x0001
    PROCESS_QUERY_INFORMATION = 0x0400

    count = 32
    while True:
        ProcessIds = (ctypes.wintypes.DWORD * count)()
        cb = ctypes.sizeof(ProcessIds)
        BytesReturned = ctypes.wintypes.DWORD()
        if EnumProcesses(ctypes.byref(ProcessIds), cb, ctypes.byref(BytesReturned)):
            if(BytesReturned.value < cb):
                break
            else:
                count *= 2
        else:
            sys.exit("Call to EnumProcesses failed")

    for index in range(int(BytesReturned.value / ctypes.sizeof(ctypes.wintypes.DWORD))):
        ProcessId = ProcessIds[index]
        if(not os.getpid() == ProcessId):
            hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, ProcessId)
            if hProcess:
                ImageFileName = (ctypes.c_char * MAX_PATH)()
                if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH) > 0:
                    exe_path = str(ImageFileName.value).replace("\\\\", "\\")
                    if(pythonw_path() in exe_path.lower()):
                        TerminateProcess(hProcess, 1)
                        return True
                CloseHandle(hProcess)
    return False
