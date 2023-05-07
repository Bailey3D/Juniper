import re


def snake_to_name(input):
    """
    Convert a snake_based string into a friendly name
    :param <str:input> The input string
    :return <str:out> Formatted string
    """
    output = ""
    for i in input.split("_"):
        output += i.capitalize() + " "
    return output


def friendly_to_code(input_, preserve_case=False):
    """
    Converts a friendly / display string to one which is valid for code
    :param <str:input> String to convert
    :param [<bool:preserve_case>] Should case be preserved?
    :return <str:converted> Converted string
    """
    output = input_ if preserve_case else input_.lower()
    output = output.rstrip(" ")
    for i in "!?£$%^&*(),.#/\\":
        output = output.replace(i, "")
    for i in " -":
        output = output.replace(i, "_")
    return output


def remove_substrings(target, *args):
    """
    Remove a list of substrings from a target string
    :param <str:target> Target string to work on
    :param <*args:args> Substrings to remove
    :return <str:string> Cleaned string
    """
    output = target
    for i in args:
        output = output.replace(i, "")
    return output


def remove_prefix(target, prefix):
    """
    Removes a prefix from a target string
    :param <str:target> Target string to work on
    :param <str:prefix> Prefix to remove
    :return <str:string> Formatted string
    """
    if target.startswith(prefix):
        return target[len(prefix):]
    return target


def truncate(string, max_chars, do_ellipsis=False):
    """
    Truncates a string to be of a max character count
    :param <str:string> The string to truncate
    :param <int:max_chars> Maximum amount of characters (including whitespaces)
    :param [<bool:do_ellipsis>] If true then a ".." is added to the end if the string is truncated
    """
    has_changed = False
    if(len(string) > max_chars):
        string = string[:max_chars]
        has_changed = True
    if(do_ellipsis and has_changed):
        string += ".."
    return string


def remove_prefix(value, prefix):
    """
    Remove a prefix from a string
    :param <str:value> The string to alter
    :param <str:prefix> The prefix to remove
    :return <str:new> The new string with the prefix removed
    """
    if(value.startswith(prefix)):
        return value[len(prefix):]
    return value


def ensure_prefix(value, prefix):
    """
    Checks the input string to see if it has a prefix - adds it if it doesn't
    :param <str:value> The string to check
    :param <str:prefix> The prefix to validate
    :return <str:new> The new string
    """
    if not value.startswith(prefix):
        value = prefix + value
    return value


def remove_suffix(value, suffix):
    """
    Remove a suffix from a string
    :param <str:suffix> The suffix to remove
    :return <str:new> The new string with the suffix removed
    """
    if(value.endswith(suffix)):
        return value[:-len(suffix)]
    return value


def ensure_suffix(value, suffix):
    """
    Checks the input string to see if it has a suffix - adds it if it doesn't
    :param <str:value> The string to check
    :param <str:suffix> The suffix to validate
    :return <str:new> The new string
    """
    if not value.endswith(suffix):
        value = suffix + value
    return value


def remove_prefix_and_suffix(value, prefix, suffix):
    """
    Remove a prefix and suffix from an input string
    :param <str:prefix> The prefix to remove
    :param <str:suffix> The suffix to remove
    :return <str:new> The new string
    """
    output = remove_prefix(value, prefix)
    output = remove_suffix(output, suffix)
    return output


def get_first_number_in_string(string):
    """
    Finds the first number stored in a string (int or float - whatever is first)
    :param <str:string> The string to search
    :return <number:output> The number if found - else None
    """
    match = re.search(r"[-+]?\d*\.?\d+", string)

    if match:
        number = match.group()
        return float(number) if (".") in number else int(number)

    return None
