import juniper.dcc.utilities.viewport
import juniper.decorators
import juniper.types.math.vector


class Node(object):
    def __init__(self, native_object):
        self.wraps = native_object

    # ------------------------------------------------------

    @property
    def name(self):
        """
        Gets the name of this node
        """
        return self.get_name()

    @juniper.decorators.virtual_method
    def get_name(self):
        raise NotImplementedError

    @get_name.override("max")
    def get_name(self):
        if(self.wraps):
            return self.wraps.name
        return ""

    # ------------------------------------------------------

    @juniper.decorators.virtual_method
    def delete(self):
        """
        Delete this node
        """
        raise NotImplementedError

    @delete.override("max")
    def delete(self):
        import pymxs
        pymxs.runtime.delete(self.wraps)

    # ------------------------------------------------------

    @juniper.decorators.virtual_method
    def select(self):
        """
        Selects this object
        """
        raise NotImplementedError

    @select.override("max")
    def select(self):
        if(self.wraps):
            import pymxs
            pymxs.runtime.selectMore(self.wraps)

    # ------------------------------------------------------

    @juniper.decorators.virtual_method
    def deselect(self):
        """
        Deselect this object
        """
        raise NotImplementedError

    @deselect.override("max")
    def deselect(self):
        import pymxs
        pymxs.runtime.deselect(self.wraps)

    # ------------------------------------------------------

    @property
    def visible(self):
        """
        Gets the visibility of this object
        :return <bool:visibility> True if visible - else False
        """
        return self.get_is_visible()

    @juniper.decorators.virtual_method
    def get_is_visible(self):
        raise NotImplementedError

    @get_is_visible.override("max")
    def get_is_visible(self):
        return not self.native_object.isHidden

    # ------------------------------------------------------

    @juniper.decorators.virtual_method
    def show(self):
        """
        Makes the current object visible
        """
        raise NotImplementedError

    @show.override("max")
    def show(self):
        import pymxs
        pymxs.runtime.unhide(self.native_object)

    @juniper.decorators.virtual_method
    def hide(self):
        """
        Makes the current object hidden
        """
        raise NotImplementedError

    @hide.override("max")
    def hide(self):
        import pymxs
        pymxs.runtime.unhide(self.native_object)

    # ------------------------------------------------------

    def focus(self):
        """
        Focuses this object in the viewport
        """
        juniper.dcc.utilities.viewport.focus(self)

    # ------------------------------------------------------

    @property
    def position(self):
        return self.get_position()

    @position.setter
    def position(self, value):
        self.set_position(value)

    @property
    def rotation(self):
        return self.get_rotation()

    @rotation.setter
    def rotation(self, value):
        self.set_rotation(value)

    @property
    def scale(self):
        return self.get_scale()

    @scale.setter
    def scale(self, value):
        self.set_scale(value)

    # ------------------------------------------------------

    @juniper.decorators.virtual_method
    def get_position(self):
        raise NotImplementedError

    @get_position.override("max")
    def get_position(self):
        native_position = self.wraps.position
        return juniper.types.math.vector.Vector3(native_position.x, native_position.y, native_position.z)

    @juniper.decorators.virtual_method
    def set_position(self, value):
        raise NotImplementedError

    @set_position.override("max")
    def set_position(self, value):
        import pymxs
        self.wraps.position = pymxs.runtime.point3(value.x, value.y, value.z)

    def translate(self, value):
        self.position = self.position + value

    def rotate(self, value):
        self.rotation = self.rotation + value

    # ------------------------------------------------------

    @juniper.decorators.virtual_method
    def get_rotation(self):
        raise NotImplementedError

    @get_rotation.override("max")
    def get_position(self):
        import pymxs
        native_rotation = pymxs.ruintime.quatToEuler(self.wraps.rotation)
        return juniper.types.math.vector.Vector3(native_rotation.x, native_rotation.y, native_rotation.z)

    @juniper.decorators.virtual_method
    def set_rotation(self, value):
        raise NotImplementedError

    @set_rotation.override("max")
    def set_rotation(self, value):
        import pymxs
        import pymxs.juniper.wrappers
        with pymxs.juniper.wrappers.CoordSys("local"):
            self.wraps.rotation = pymxs.runtime.eulerAngles(value.x, value.y, value.z)

    # ------------------------------------------------------

    @juniper.decorators.virtual_method
    def get_scale(self):
        raise NotImplementedError

    @get_scale.override("max")
    def get_position(self):
        native_scale = self.wraps.scale
        return juniper.types.math.vector.Vector3(native_scale.x, native_scale.y, native_scale.z)

    @juniper.decorators.virtual_method
    def set_scale(self, value):
        raise NotImplementedError

    @set_scale.override("max")
    def set_scale(self, value):
        import pymxs
        self.wraps.scale = pymxs.runtime.point3(value.x, value.y, value.z)
