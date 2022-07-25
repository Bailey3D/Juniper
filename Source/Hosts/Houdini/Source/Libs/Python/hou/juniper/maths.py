import hou


def lerp(a, b, f):
    return (a * (1.0 - f)) + (b * f)


def lerp_vector3(a, b, f):
    return hou.Vector3(
        lerp(a.x(), b.x(), f),
        lerp(a.y(), b.y(), f),
        lerp(a.z(), b.z(), f)
    )


def safe_div(x, y):
    return x / (y if y != 0.0 else 0.0001)


def remap(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * safe_div((value - start1), (stop1 - start1))


def remap_vector3(value, start1, stop1, start2, stop2):
    return hou.Vector3(
        remap(value.x(), start1.x(), stop1.x(), start2.x(), stop2.x()),
        remap(value.y(), start1.y(), stop1.y(), start2.y(), stop2.y()),
        remap(value.z(), start1.z(), stop1.z(), start2.z(), stop2.z())
    )


def average_vector3(values):
    output = hou.Vector3(0.0, 0.0, 0.0)
    for i in values:
        output += i
    return output / len(values)
