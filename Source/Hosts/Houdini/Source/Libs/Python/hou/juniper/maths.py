import hou

import juniper.math


def lerp_vector3(a, b, f):
    return hou.Vector3(
        juniper.math.lerp(a.x(), b.x(), f),
        juniper.math.lerp(a.y(), b.y(), f),
        juniper.math.lerp(a.z(), b.z(), f)
    )


def remap_vector3(value, start1, stop1, start2, stop2):
    return hou.Vector3(
        juniper.math.remap(value.x(), start1.x(), stop1.x(), start2.x(), stop2.x()),
        juniper.math.remap(value.y(), start1.y(), stop1.y(), start2.y(), stop2.y()),
        juniper.math.remap(value.z(), start1.z(), stop1.z(), start2.z(), stop2.z())
    )


def average_vector3(values):
    output = hou.Vector3(0.0, 0.0, 0.0)
    for i in values:
        output += i
    return output / len(values)
