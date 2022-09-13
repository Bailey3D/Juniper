import juniper.decorators
import jdcc.scene.object_wrapper


class SelectionSetWrapper(object):
    def __init__(self, native_object):
        self.native_object = native_object

    # ----------------------------------------------------------------

    @property
    def objects(self):
        """
        Gets all objects in this selection set
        :return <[ObjectWrapper]:objects> All of the objects in this selection set
        """
        return self.get_objects()

    @juniper.decorators.virtual_method
    def get_objects(self):
        raise NotImplementedError

    @get_objects.override("max")
    def __get_objects(self):
        output = []
        objects = [x for x in self.native_object]
        for i in objects:
            object_wrapper = jdcc.scene.object_wrapper.ObjectWrapper(i)
            output.append(object_wrapper)
        return output

    # ----------------------------------------------------------------

    @property
    def name(self):
        """
        Gets the name of this selection set
        :return <str:name> The name of this selection set
        """
        return self.get_name()

    @name.setter
    def name(self, value):
        """
        Sets the name of this selection set
        :param <str:value> The new name
        """
        self.set_name(value)

    @juniper.decorators.virtual_method
    def get_name(self):
        raise NotImplementedError

    @get_name.override("max")
    def __get_name(self):
        return self.native_object.name

    @juniper.decorators.virtual_method
    def set_name(self, value):
        raise NotImplementedError

    @set_name.override("max")
    def __set_name(self, value):
        self.native_object.name = value

    # ----------------------------------------------------------------

    @juniper.decorators.virtual_method
    def add_object(self, object_):
        """
        Adds an object to this selection set
        :param <ObjectWrapper:object_> The object to add
        """
        raise NotImplementedError

    @add_object.override("max")
    def __add_object(self, object_):
        import pymxs
        import pymxs.juniper.maxscript
        current_nodes = [x for x in self.native_object]
        current_nodes.append(object_.native_object)
        current_nodes = pymxs.juniper.maxscript.python_to_maxscript_array(current_nodes)
        pymxs.runtime.selectionSets[self.name] = current_nodes

    # ----------------------------------------------------------------

    def hide(self):
        """
        Hides all nodes in this selection set
        """
        for i in self.objects:
            i.hide()

    def show(self):
        """
        Shows all nodes in this selection set
        """
        for i in self.objects:
            i.show()

    def select(self):
        """
        Selects all nodes in this selection set
        """
        for i in self.objects:
            i.select()

    def unselect(self):
        """
        Unselects all nodes in this selection set
        """
        for i in self.objects:
            i.unselect()
