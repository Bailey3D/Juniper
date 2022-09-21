"""
Library containing filesystem based functions
"""
import os
import pathlib
import traceback as traceback_
import stat
import _winapi
import ctypes

from qtpy import QtWidgets

import juniper
import juniper.widgets


kernel32 = ctypes.WinDLL('kernel32')


def remove_readonly(src):
    """
    Remove the read only flag froma path
    :param <str:src> Source file/directory
    """
    os.chmod(src, stat.S_IWRITE)


def resolve_path(target):
    """
    Return the real path for an input path
    Currently this has to be used as PYthon3.7 doesn't return the correctly
    resolved path for subst drives when using os.path.realpath
    :param <str:target> Target path to resolve
    :return <str:path> Resolved path
    """
    return str(pathlib.Path(target).resolve())


def show_in_explorer(path):
    """
    Reveal a file in windows explorer
    :param <str:path> The absolute path to the file
    """
    if(os.path.isdir(path)):
        os.startfile(path)
    elif(os.path.isfile(path)):
        os.startfile(os.path.dirname(path))


def makedir(path):
    """
    Creates a folder if it doesn't already exist\n
    :param <str:path> The path of the directory to make\n
    """
    if(not os.path.isdir(path)):
        os.makedirs(path)


def makesubdirs(folder_dir, *subdirs):
    """
    Makes a list of subdirectories inside an input directory\n
    :param <str:folder_dir> The parent directory\n
    :param <[str]:subdirs> Names of the child subdirectories to create\n
    """
    if(not subdirs):
        makedir(folder_dir)
    if(len(subdirs) == 1):
        if(type(subdirs[0]) == list):
            subdirs = subdirs[0]
    makedir(folder_dir)
    for i in subdirs:
        makedir(os.path.join(folder_dir, i))


def pick_folder(title="Pick Folder..", start="C:\\"):
    """
    Open a basic Qt based folder picker dialog\n
    :param <str:title> Title of the folder picker window\n
    :param <str:start> Starting directory of the folder picker\n
    :return <str:path> The pack to the picked directory\n
    """
    juniper.widgets.get_application()
    file_dialog = QtWidgets.QFileDialog()
    open_dir = file_dialog.getExistingDirectory(
        None,
        title,
        start
    )
    if(len(open_dir)):
        return open_dir
    return ""


def pick_file(title="Pick File..", start="C:\\", file_types=""):
    """
    Open a basic Qt based file picker dialog\n
    :param <str:title> Title of the file picker window\n
    :param <str:start> Starting directory of the file picker\n
    :param <str:file_types> Standard windows file type constructor (Ie, "Text Files (*.txt), *.txt"\n
    :return <str:path> The path to the picked file\n
    """
    juniper.widgets.get_application()
    file_dialog = QtWidgets.QFileDialog()
    open_file = file_dialog.getOpenFileName(
        None,
        title,
        start,
        file_types
    )[0]
    return open_file


def pick_files(title="Pick Files..", start="C:\\", file_types=""):
    """
    Open a basic Qt based file picker dialog\n
    :param <str:title> Title of the file picker window\n
    :param <str:start> Starting directory of the file picker\n
    :param <str:file_types> Standard windows file type constructor (Ie, "Text Files (*.txt), *.txt"\n
    :return <str:path> The path to the picked file\n
    """
    juniper.widgets.get_application()
    file_dialog = QtWidgets.QFileDialog()
    open_file = file_dialog.getOpenFileNames(
        None,
        title,
        start,
        file_types
    )[0]
    return open_file


def symlink(src, dest):
    """
    Create a symlink between 2 paths\n
    :param <str:src> Source file path\n
    :param <str:dest> Destination file path\n
    """
    src_ = resolve_path(src)
    dest_ = resolve_path(dest)
    try:
        makedir(os.path.dirname(dest_))

        if(os.path.isdir(src_)):
            if(os.path.islink(dest_)):
                os.unlink(dest_)
            os.symlink(
                os.path.realpath(src_),
                os.path.realpath(dest_),
                target_is_directory=False)
    except OSError as error:
        tb = traceback_.extract_stack()[0]  # traceback from where this function was called - not where the log is called
        if(os.path.isdir(dest)):
            juniper.log.warning(f"Symlink Failed: Destination already exists - {dest}", traceback_stack=tb)
        elif(not os.path.isdir(src)):
            juniper.log.error(f"Symlink Failed: Source directory does not exist - {src}", traceback_stack=tb)
        else:
            juniper.log.error(f"Symlink Failed: {error}", traceback_stack=tb)
    else:
        juniper.log.info("Symlink Created Successfully")


def is_junction(directory):
    """
    Check if a directory is a junction
    :param <str:directory> The directory to check
    :return <bool:state> True if the directory is a junction - else False
    """
    if(not os.path.isdir(directory) or os.path.islink(directory)):
        return False
    result = kernel32.GetFileAttributesW(directory)
    if(result == 0xFFFFFFFF):
        return False
    return bool(result & 0x00400)


def remove_junction(directory):
    """
    Removes a junction
    :param <str:directory> The junction directory to remove
    """
    if(is_junction(directory)):
        os.rmdir(directory)


def create_junction(src, dest):
    """
    Creates a junction between 2 directories\n
    :param <str:src> Source directory\n
    :param <str:dest> Destination directory\n
    """
    src_ = resolve_path(src)

    try:
        if(is_junction(dest)):
            remove_junction(dest)
        _winapi.CreateJunction(
            os.path.realpath(src_),
            os.path.realpath(dest)
        )
    except OSError as error:
        tb = traceback_.extract_stack()[0]  # traceback from where this function was called - not where the log is called
        if(os.path.isdir(dest)):
            juniper.log.warning(f"Junction Creation Failed: Destination already exists - {dest}", traceback_stack=tb)
        elif(not os.path.isdir(src)):
            juniper.log.error(f"Junction Creation Failed: Source directory does not exist - {src}", traceback_stack=tb)
        else:
            juniper.log.error(f"Junction Creation Failed: {error}", traceback_stack=tb)
    else:
        juniper.log.info("Junction Creation Created Successfully")


def remove_read_only(path):
    """
    Removes the read only flag from a file
    :param <str:path> The path to edit
    """
    if(os.path.isfile(path) or os.path.isdir(path)):
        os.chmod(path, stat.S_IWRITE)
