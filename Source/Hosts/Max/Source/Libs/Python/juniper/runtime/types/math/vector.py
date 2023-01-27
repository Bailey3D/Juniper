import pymxs

import juniper.runtime.types.math.vector


class Vector2(juniper.runtime.types.math.vector.Vector2):
    def get_native_object(self):
        return pymxs.runtime.Point2(self.x, self.y)

    def _from_native_object(self, native_object):
        return list((native_object.x, native_object.y))


class Vector3(juniper.runtime.types.math.vector.Vector3):
    def get_native_object(self):
        return pymxs.runtime.Point3(self.x, self.y, self.z)

    def _from_native_object(self, native_object):
        return list((native_object.x, native_object.y, native_object.z))


class Vector4(juniper.runtime.types.math.vector.Vector4):
    def get_native_object(self):
        return pymxs.runtime.Point4(self.x, self.y, self.z, self.w)

    def _from_native_object(self, native_object):
        return list((native_object.x, native_object.y, native_object.z, native_object.w))
