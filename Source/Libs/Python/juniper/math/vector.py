"""
Wrapper for a simple vector type
"""
import math

import juniper.decorators


class _VectorType(object):
    def __init__(self, *args):
        """
        Base class for a Vector type
        """
        if(len(args) == 1):
            self._data = self._from_native_object(args[0])
        else:
            self._data = list(args)

    # -----------------------------------------------------

    def __repr__(self):
        return f"{type(self).__name__}{tuple(self._data)}"

    def __getitem__(self, index):
        key = ("x", "y", "z", "w")[index]
        return eval(f"self.{key}")

    def __len__(self):
        return len(self._data)

    def __floordiv__(self, other):
        if(isinstance(other, self.__class__)):
            return self.__class__(*(a // b for a, b in zip(self, other)))
        elif(type(other) in (int, float)):
            return self.__class__(*(a // other for a in self))
        else:
            return NotImplemented

    def __truediv__(self, other):
        if(isinstance(other, self.__class__)):
            return self.__class__(*(a / b for a, b in zip(self, other)))
        elif(type(other) in (int, float)):
            return self.__class__(*(a / other for a in self))
        else:
            return NotImplemented

    def __mul__(self, other):
        if(isinstance(other, self.__class__)):
            return self.__class__(*(a * b for a, b in zip(self, other)))
        elif(type(other) in (int, float)):
            return self.__class__(*(a * other for a in self))
        else:
            return NotImplemented

    def __rmul__(self, other):
        if(isinstance(other, self.__class__)):
            return self.__class__(*(a * b for a, b in zip(self, other)))
        elif(type(other) in (int, float)):
            return self.__class__(*(a * other for a in self))
        else:
            return NotImplemented

    def __add__(self, other):
        if(isinstance(other, self.__class__)):
            return self.__class__(*(a + b for a, b in zip(self, other)))
        elif(type(other) in (int, float)):
            return self.__class__(*(a + other for a in self))
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if(isinstance(other, self.__class__)):
            return self.__class__(*(a - b for a, b in zip(self, other)))
        elif(type(other) in (int, float)):
            return self.__class__(*(a - other for a in self))
        else:
            return NotImplemented

    def __rsub__(self, other):
        if(isinstance(other, self.__class__)):
            return self.__class__(*(b - a for a, b in zip(self, other)))
        elif(type(other) in (int, float)):
            return self.__class__(*(other - a for a in self))
        else:
            return NotImplemented

    def __neg__(self):
        return self * -1

    def __pos__(self):
        return self

    def __abs__(self):
        return self.__class__(*(abs(x) for x in self))

    # -----------------------------------------------------

    def __getattr__(self, key):
        if(self.__swizzle_check(key)):
            return self.__swizzle_get(key)
        else:
            raise AttributeError

    def __setattr__(self, key, value):
        if(self.__swizzle_check(key)):
            self.__swizzle_set(key, value)
        else:
            super(_VectorType, self).__setattr__(key, value)

    # -----------------------------------------------------

    def __swizzle_check(self, swizzle_keys):
        """
        Check if the input key is a valid type for swizzling this vector
        :return <bool:swizzleable> True if the key can swizzle - else False
        """
        if(len(swizzle_keys) <= 4 and len(swizzle_keys) > 1):
            for i in swizzle_keys:
                if(i not in "xyzw"):
                    return False
            return True
        return False

    def __swizzle_get(self, swizzle_keys):
        output = None

        if(len(swizzle_keys) == 1):
            output = eval(f"self.{swizzle_keys[0]}")
        else:
            values = []
            for i in range(len(swizzle_keys)):
                values.append(eval(f"self.{swizzle_keys[i]}"))
            output = eval(f"Vector{len(swizzle_keys)}{tuple(values)}")

        return output

    def __swizzle_set(self, swizzle_keys, new_values_vector):
        if(len(swizzle_keys) == 1):
            exec(f"self.{swizzle_keys[0]} = {new_values_vector}")
        else:
            for i in range(len(swizzle_keys)):
                exec(f"self.{swizzle_keys[i]} = {new_values_vector[i]}")

    # -----------------------------------------------------

    @property
    def native_object(self):
        """
        Gets a version of this as the native type for the current DCC

        Note:   When overriding this in child classes the `get_native_object` method must be defined 
                in the class body just so we have access to an instance of the function to override

        :return <value:native_type> The native type where possible - else None
        """
        return self.get_native_object()

    @juniper.decorators.virtual_method
    def get_native_object(self):
        raise NotImplementedError

    @juniper.decorators.virtual_method
    def _from_native_object(self, native_object):
        """
        Creates a new instance of this type from the input type
        """
        raise NotImplementedError

    # -----------------------------------------------------

    @property
    def x(self):
        return self._data[0]

    @x.setter
    def x(self, value):
        self._data[0] = value

    @property
    def y(self):
        return self._data[1]

    @y.setter
    def y(self, value):
        self._data[1] = value

    @property
    def z(self):
        return self._data[2]

    @z.setter
    def z(self, value):
        self._data[2] = value

    @property
    def w(self):
        return self._data[3]

    @w.setter
    def w(self, value):
        self._data[3] = value

    # -----------------------------------------------------

    @property
    def length_squared(self):
        """
        The squared length / magnitude of this vector
        Use this when the euclidean length is not needed to avoid sqrt calculation
        :return <float:length_squared> The squared length of this vector
        """
        return sum(a * a for a in self._data)

    @property
    def length(self):
        """
        The euclidean length / magnitude of this vector
        For situations where euclidean length is not needed use `length_squared` to avoid the sqrt calculation
        :return <float:length> The length of this vector
        """
        return math.sqrt(self.length_squared)

    @property
    def normalized(self):
        """
        Get a normalized copy of this vector
        :return <_VectorType:normalized> Normalized version of this vector
        """
        return self / self.length

    @property
    def sum(self):
        """
        Get the sum of all components of this vector
        :return <float:sum> The sum of all components
        """
        return sum(self._data)

    def distance_squared(self, other):
        """
        The suqared distance between two vectors
        Use this when euclidean length is not needed to avoid the sqrt calculation
        :param <_VectorType:other> The other vector
        :return <float:distance> The distance between two vectors
        """
        if(isinstance(other, self.__class__)):
            return (self - other).length_squared
        else:
            return NotImplementedError

    def distance(self, other):
        """
        The euclidean distance between two vectors
        :param <_VectorType:other> The other vector
        :return <float:distance> The distance between two vectors
        """
        if(isinstance(other, self.__class__)):
            return (self - other).length
        else:
            return NotImplementedError

    def dot(self, other):
        """
        The dot product of this vector and another vector
        :param <_VectorType:other> The other vector
        :return <float:dot> The dot product
        """
        if(isinstance(other, self.__class__)):
            return sum(a * b for a, b in zip(self, other))
        else:
            return NotImplementedError


class Vector2(_VectorType):
    def __init__(self, *args):
        super(Vector2, self).__init__(*args)

    # -----------------------------------------------------

    @juniper.decorators.virtual_method
    def get_native_object(self):
        raise NotImplementedError

    @juniper.decorators.virtual_method
    def _from_native_object(self, native_object):
        raise NotImplementedError

    @_from_native_object.override("max")
    def __from_native_object(self, native_object):
        return list((native_object.x, native_object.y))

    @get_native_object.override("max")
    def _get_native_object(self):
        import pymxs
        return pymxs.runtime.Point2(self.x, self.y)

    # -----------------------------------------------------


class Vector3(_VectorType):
    def __init__(self, *args):
        super(Vector3, self).__init__(*args)

    def cross(self, other):
        """
        The cross product of this vector and another vector
        :param <_VectorType:other> The other vector
        :return <_VectorType:cross> The crossed vector
        """
        if(isinstance(other, self.__class__)):
            return Vector3(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x
            )
        else:
            return NotImplementedError

    # -----------------------------------------------------

    @juniper.decorators.virtual_method
    def get_native_object(self):
        raise NotImplementedError

    @juniper.decorators.virtual_method
    def _from_native_object(self, native_object):
        raise NotImplementedError

    @_from_native_object.override("max")
    def __from_native_object(self, native_object):
        return list((native_object.x, native_object.y, native_object.z))

    @get_native_object.override("max")
    def _get_native_object(self):
        import pymxs
        return pymxs.runtime.Point3(self.x, self.y, self.z)

    # -----------------------------------------------------

    @juniper.decorators.program_context("ue4")
    def as_linear_color(self):
        import unreal
        return unreal.LinearColor(r=self.x, g=self.y, b=self.z, a=1.0)


class Vector4(_VectorType):
    def __init__(self, *args):
        super(Vector4, self).__init__(*args)

    # -----------------------------------------------------

    @juniper.decorators.virtual_method
    def get_native_object(self):
        raise NotImplementedError

    @juniper.decorators.virtual_method
    def _from_native_object(self, native_object):
        raise NotImplementedError

    @_from_native_object.override("max")
    def __from_native_object(self, native_object):
        return list((native_object.x, native_object.y, native_object.z, native_object.w))

    @get_native_object.override("max")
    def _get_native_object(self):
        import pymxs
        return pymxs.runtime.Point4(self.x, self.y, self.z, self.w)

    @juniper.decorators.program_context("ue4")
    def as_linear_color(self):
        import unreal
        return unreal.LinearColor(r=self.x, g=self.y, b=self.z, a=self.w)
