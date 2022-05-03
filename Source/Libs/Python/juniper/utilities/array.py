"""
Array based helper functions
"""


def consolidate_array(*args):
    """
    Converts an input to a single 1d array
    :param <*args:args> Input arguments to flatten
    :return <list:output> The consolidated arrays
    """
    output = []
    for i in args:
        if(type(i) in (set, list, tuple)):
            output += consolidate_array(*i)
        else:
            output.append(i)
    return output
