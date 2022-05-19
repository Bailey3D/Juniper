import juniper.decorators
import juniper.types.wrappers.type_wrapper
from juniper.types.math.vector import Vector3


class ObjectWrapperManager(juniper.types.wrappers.type_wrapper.TypeWrapperManager):
    pass


class ObjectWrapper(juniper.types.wrappers.type_wrapper.TypeWrapper):
    __manager__ = ObjectWrapperManager

    # -------------------------------------------------------

    @property
    def name(self):
        """
        :return <str:name> The name of the current object
        """
        return self.get_name()

    @juniper.decorators.virtual_method
    def get_name(self):
        raise NotImplementedError

    @get_name.override("max")
    def _get_name(self):
        if(self.native_object):
            return self.native_object.name
        return ""

    # -------------------------------------------------------

    @juniper.decorators.virtual_method
    def delete(self):
        """
        Delete this node
        """
        raise NotImplementedError

    @delete.override("max")
    def _delete(self):
        import pymxs
        pymxs.runtime.delete(self.native_object)

    # -------------------------------------------------------

    @juniper.decorators.virtual_method
    def select(self):
        """
        Selects this object
        """
        raise NotImplementedError

    @select.override("max")
    def _select(self):
        if(self.native_object):
            import pymxs
            pymxs.runtime.selectMore(self.native_object)

    @juniper.decorators.virtual_method
    def unselect(self):
        """
        Unselect this object
        """
        raise NotImplementedError

    @unselect.override("max")
    def _unselect(self):
        import pymxs
        pymxs.runtime.deselect(self.native_object)

    # -------------------------------------------------------

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
    def _get_is_visible(self):
        return not self.native_object.isHidden

    @juniper.decorators.virtual_method
    def show(self):
        """
        Makes the current object visible
        """
        raise NotImplementedError

    @show.override("max")
    def _show(self):
        import pymxs
        pymxs.runtime.unhide(self.native_object)

    @juniper.decorators.virtual_method
    def hide(self):
        """
        Makes the current object hidden
        """
        raise NotImplementedError

    @hide.override("max")
    def _hide(self):
        import pymxs
        pymxs.runtime.unhide(self.native_object)

    # -------------------------------------------------------

    @juniper.decorators.virtual_method
    def focus(self):
        """
        Focus this object in the viewport
        """
        import juniper_dcc.viewport
        juniper_dcc.viewport.focus(self)

    # -------------------------------------------------------

    @juniper.decorators.virtual_method
    def copy(self):
        """
        Copies this object and all of its properties
        :return <ObjectWrapper:new_object> The copied object - or None if it was not copied
        """
        raise NotImplementedError

    @copy.override("max")
    def _copy(self):
        import juniper_max.scene
        copy = juniper_max.scene.clone(self.native_object, copy=True, deep_clone=True)
        if(len(copy)):
            return ObjectWrapper(copy[0])
        return None

    @juniper.decorators.virtual_method
    def instance(self):
        """
        Creates an instance of this object if it is possible in the current DCC context
        :return <ObjectWrapper:new_object> The instanced object - or None if it was not instanced
        """
        raise NotImplementedError

    @instance.override("max")
    def _instance(self):
        import juniper_max.scene
        instance = juniper_max.scene.clone(self.native_object, instance=True, deep_clone=True)
        if(len(instance)):
            return ObjectWrapper(instance[0])
        return None

    @juniper.decorators.virtual_method
    def reference(self):
        """
        Creates an reference of this object if it is possible in the current DCC context
        :return <ObjectWrapper:new_object> The referenced object - or None if it was not referenced
        """
        raise NotImplementedError

    @reference.override("max")
    def _reference(self):
        import juniper_max.scene
        reference = juniper_max.scene.clone(self.native_object, reference=True, deep_clone=True)
        if(len(reference)):
            return ObjectWrapper(reference[0])
        return None

    # -------------------------------------------------------

    @juniper.decorators.virtual_method
    def translate(self, amount):
        raise NotImplementedError

    @translate.override("max")
    def _translate(self, amount):
        self.position = self.position + amount

    @juniper.decorators.virtual_method
    def rotate(self, amount):
        raise NotImplementedError

    @rotate.override("max")
    def _rotate(self, amount):
        self.rotation = self.position + amount

    # -------------------------------------------------------

    @property
    def position(self):
        return self.get_position()

    @position.setter
    def position(self, value):
        self.set_position(value)

    @juniper.decorators.virtual_method
    def get_position(self):
        raise NotImplementedError

    @get_position.override("max")
    def _get_position(self):
        return Vector3(self.native_object.position)

    @juniper.decorators.virtual_method
    def set_position(self, value):
        raise NotImplementedError

    @set_position.override("max")
    def _set_position(self, value):
        self.native_object.position = value.native_object

    # -------------------------------------------------------

    @property
    def rotation(self):
        """
        Gets the world rotation of this object in euler angles
        :return <Vector3:rotation> The euler rotation of this object
        """
        return self.get_rotation()

    @rotation.setter
    def rotation(self, value):
        self.set_rotation(value)

    @juniper.decorators.virtual_method
    def get_rotation(self):
        raise NotImplementedError

    @get_rotation.override("max")
    def _get_rotation(self):
        import pymxs
        return Vector3(pymxs.runtime.quatToEuler(self.native_object.rotation))

    @juniper.decorators.virtual_method
    def set_rotation(self, value):
        raise NotImplementedError

    @set_rotation.override("max")
    def _set_rotation(self, value):
        import pymxs
        import juniper_max.wrappers
        with juniper_max.wrappers.CoordSys("local"):
            import pymxs
            self.native_object.rotation = pymxs.runtime.eulerAngles(
                value.x,
                value.y,
                value.z
            )

    # -------------------------------------------------------

    @property
    def scale(self):
        return self.get_scale()

    @scale.setter
    def scale(self, value):
        self.set_scale(value)

    @juniper.decorators.virtual_method
    def get_scale(self):
        raise NotImplementedError

    @get_scale.override("max")
    def _get_scale(self):
        return Vector3(self.native_object.scale)

    @juniper.decorators.virtual_method
    def set_scale(self, value):
        raise NotImplementedError

    @set_scale.override("max")
    def _set_scale(self, value):
        self.native_object.scale = value.native_object
