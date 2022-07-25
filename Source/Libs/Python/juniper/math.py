"""
Math based helper functions
"""


def clamp(number, min_, max_):
    """
    Saturates a number (clamp between [0..1])
    :param <number:number> The number to saturate
    :param <number:min_> Minimum value for this number
    :param <number:max_> Maximum value for this number
    :return <number:saturated> The saturated number
    """
    if(number > max_):
        return max_
    elif(number < min_):
        return min_
    return number


def saturate(number):
    """
    Saturates a number (clamp between [0..1])
    :param <number:number> The number to saturate
    :return <number:saturated> The saturated number
    """
    return clamp(number, 0.0, 1.0)
