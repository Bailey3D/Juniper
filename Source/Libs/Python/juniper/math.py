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


def safe_div(x, y):
    """
    Division with a safety check for division by 0
    :param <number:x> left hand side value
    :param <number:y> right hand side value
    :return <float:output> The division result
    """
    return x / (y if y != 0.0 else 0.0001)


def lerp(a, b, x):
    """
    Lerps a number value
    :param <number:a> The lower value to lerp to
    :param <number:b> The higher value to lerp to
    :param <number:x> The alpha to lerp
    :return <float:value> The lerped value
    """
    return (a * (1.0 - x)) + (b * x)


def remap(value, start, stop, target_start, target_stop):
    """
    Remaps a value from [start..stop] to [target_start..target_stop]
    :param <number:value> The value to remap
    :param <number:start> The existing start value
    :param <number:stop> The existing stop value
    :param <number:target_start> The target start value
    :param <number:target_stop> The target stop value
    :return <number:remapped> The number remapped
    """
    return target_start + (target_stop - target_start) * safe_div((value - start), (stop - start))
