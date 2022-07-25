# TODO! Delete?
import pymxs


def get_type(native_object):
    if(type(native_object) != pymxs.MXSWrapperBase):
        return type(native_object)
    return pymxs.runtime.classOf(native_object)


# ------------------------------------------------------------------

def point4_to_vector4(native_object):
    import juniper.types.math.vector
    return juniper.types.math.vector.Vector4(
        native_object.x,
        native_object.y,
        native_object.z,
        native_object.w
    )


def point3_to_vector3(native_object):
    import juniper.types.math.vector
    return juniper.types.math.vector.Vector3(
        native_object.x,
        native_object.y,
        native_object.z
    )


def point2_to_vector2(native_object):
    import juniper.types.math.vector
    return juniper.types.math.vector.Vector2(
        native_object.x,
        native_object.y
    )


# ------------------------------------------------------------------


def vector4_native(juniper_object):
    return pymxs.runtime.point4(
        juniper_object.x,
        juniper_object.y,
        juniper_object.z,
        juniper_object.w
    )


def point3_from_vector3(juniper_object):
    return pymxs.runtime.point4(
        juniper_object.x,
        juniper_object.y,
        juniper_object.z
    )


def point2_from_vector2(juniper_object):
    return pymxs.runtime.point4(
        juniper_object.x,
        juniper_object.y
    )
