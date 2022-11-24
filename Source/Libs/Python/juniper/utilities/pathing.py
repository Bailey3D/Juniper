import os
import pathlib


def set_path_file_type(filepath, filetype):
    """
    Sets the file type on a filepath\n
    :param <str:filepath> The filepath to set on\n
    :param <str:filetype> The new filetype\n
    """
    return (filepath.split(".")[0] + "." + filetype.replace(".", ""))


def remove_file_type(filepath):
    """
    Remove the file type from a string\n
    :param <str:filepath> The filepath to strip from\n
    :return <str:path> Filepath with type removed\n
    """
    return filepath.rsplit(".", 1)[0]


def get_filename_only(filepath):
    """
    Strip only the filename out of an input path\n
    :param <str:filepath> The filepath to strip from\n
    :return <str:name> The filename\n
    """
    return os.path.splitext(os.path.basename(filepath))[0]


def sanitize_path(filepath):
    """
    Formats a filepath to use standardized pathing
    :param <str:filepath> The path to sanetize
    :return <str:output> The sanitized path
    """
    output = filepath.replace("/", "\\")
    return output


def is_valid_path(path):
    """
    Checks if a path is valid (aka whether it could exist - not if it does)
    :param <str:path> The path to check (this can be a directory or a file)
    :return <bool:validity> True if this path is valid - else False
    """
    output = False
    if(path.encode("utf-8").decode("utf-8", "ignore") == path):
        try:
            pathlib.Path(path).resolve()
            output = True
        except Exception:
            pass
    return output
