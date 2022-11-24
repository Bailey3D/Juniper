import juniper.dcc.types.scene.node
import juniper.decorators
import juniper.types.framework.singleton


class SelectionSetManager(juniper.types.framework.singleton.Singleton):
    def __init__(self):
        pass

    @juniper.decorators.virtual_method
    def remove_empty_sets(self):
        """
        Deletes all selection sets which do not contain any Nodes
        """
        raise NotImplementedError

    @remove_empty_sets.override("max")
    def remove_empty_sets(self):
        import pymxs
        deleted_set_names = []
        sel_sets = pymxs.runtime.selectionSets

        for i in range(len(sel_sets) - 1, -1, -1):
            ss = sel_sets[i]
            nodes = [x for x in ss if pymxs.runtime.isValidNode(x)]
            if(not len(nodes)):
                pymxs.runtime.deleteItem(sel_sets, i + 1)
                deleted_set_names.append(ss.name)
        return deleted_set_names


class SelectionSet(object):
    def __init__(self, name):
        self.__name = name

    # ----------------------------------------------------------------

    @property
    def native_object(self):
        """
        Gets the application native object for this selection set
        """
        return self.__get_native_object()

    @juniper.decorators.virtual_method
    def __get_native_object(self):
        raise NotImplementedError

    @__get_native_object.override("max")
    def __get_native_object(self):
        import pymxs
        for i in pymxs.runtime.selectionSets:
            if(i.name == self.name):
                return i
        return None

    # ----------------------------------------------------------------

    @property
    def name(self):
        """
        :return <str:name> The name of this selection set
        """
        return self.__name

    @name.setter
    def name(self, value):
        """
        Sets the name of this selection set
        :param <str:value> The new name
        """
        self.set_name(value)
        self.__name = value

    @juniper.decorators.virtual_method
    def __set_name(self, value):
        raise NotImplementedError

    @__set_name.override("max")
    def __set_name(self, value):
        self.native_object.name = value

    # ----------------------------------------------------------------

    def nodes(self):
        """
        Gets all nodes in this selection set
        :return <[Node]:nodes> All nodes in this selection set
        """
        return self.__get_nodes()

    @juniper.decorators.virtual_method
    def __get_nodes(self):
        raise NotImplementedError

    @__get_nodes.override("max")
    def __get_nodes(self):
        output = []
        objects = [x for x in self.native_object]
        for i in objects:
            node = juniper.dcc.types.scene.node.Node(i)
            output.append(node)
        return output

    # ----------------------------------------------------------------

    @juniper.decorators.virtual_method
    def add_node(self, node):
        """
        Adds a node to this selection set
        :param <Node:node> The node to add
        """
        raise NotImplementedError

    @add_node.override("max")
    def add_node(self, node):
        import pymxs
        import pymxs.juniper.maxscript
        current_nodes = [x for x in self.native_object]
        current_nodes.append(node.wraps)
        current_nodes = pymxs.juniper.maxscript.python_to_maxscript_array(current_nodes)
        pymxs.runtime.selectionSets[self.name] = current_nodes

    # ----------------------------------------------------------------

    @juniper.decorators.virtual_method
    def delete(self):
        """
        Deletes this selection set
        """
        raise NotImplementedError

    @delete.override("max")
    def delete(self):
        import pymxs
        sel_sets = pymxs.runtime.selectionSets
        for i in range(len(sel_sets) - 1, -1, -1):
            ss = sel_sets[i]

            if(ss.name == self.name):
                pymxs.runtime.deleteItem(sel_sets, i + 1)
                return True
        return False

    # ----------------------------------------------------------------

    def hide(self):
        """
        Hides all nodes in this selection set
        """
        for i in self.nodes:
            i.hide()

    def show(self):
        """
        Shows all nodes in this selection set
        """
        for i in self.nodes:
            i.show()

    def select(self):
        """
        Selects all nodes in this selection set
        """
        for i in self.nodes:
            i.select()

    def deselect(self):
        """
        Deselect all nodes in this selection set
        """
        for i in self.nodes:
            i.deselect()
