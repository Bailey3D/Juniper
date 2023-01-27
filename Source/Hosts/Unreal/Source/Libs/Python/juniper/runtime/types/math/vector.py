import unreal

import juniper.runtime.types.math.vector


class Vector3(juniper.runtime.types.math.vector.Vector3):
    def as_linear_color(self):
        return unreal.LinearColor(r=self.x, g=self.y, b=self.z, a=1.0)


class Vector4(juniper.runtime.types.math.vector.Vector4):
    def as_linear_color(self):
        return unreal.LinearColor(r=self.x, g=self.y, b=self.z, a=self.w)
