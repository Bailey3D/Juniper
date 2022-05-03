import pymxs


def python_to_maxscript_array(python_array):
    """
    Converts a python based array to a maxscript one
    :param <[type]:python_array> The python array to convert
    :param <#():mxs_array> The maxscript array
    """
    output = pymxs.runtime.array()
    for i in python_array:
        pymxs.runtime.append(output, i)
    return output
