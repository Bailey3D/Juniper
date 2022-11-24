import juniper.decorators
import juniper.dcc.types.scene_graph.node


class SceneGraph(object):
    def __init__(self, wraps):
        self.__wraps = wraps

    @property
    def wraps(self):
        """
        Gets the native object for the graph which is being wrapped
        """
        return self.get_wraps

    @juniper.decorators.virtual_method
    def get_wraps(self):
        raise NotImplementedError

    @get_wraps.override("designer")
    def get_wraps(self):
        import sd
        if(not self.__wraps):
            uimgr = sd.getContext().getSDApplication().getQtForPythonUIMgr()
            return uimgr.getCurrentGraph()
        return self.__wraps

    # ---------------------------------------------------------------

    @property
    def name(self):
        """
        Gets the name of this graph
        :return <str:name> The name of the graph - "" if invalid
        """
        pass

    @juniper.decorators.virtual_method
    def get_name(self):
        raise NotImplementedError

    @get_name.override("designer")
    def get_name(self):
        import sd.api.sdproperty
        if(self.wraps):
            return self.wraps.getPropertyValueFromId(
                "identifier",
                sd.api.sdproperty.SDPropertyCategory.Annotation
            ).get()
        return ""

    # ---------------------------------------------------------------

    @property
    def outputs(self):
        # TODO~
        pass

    # ---------------------------------------------------------------

    @property
    def selection(self):
        """
        :return <[Node]:selection> All selected GraphNodes
        """
        return self.get_selection()

    @juniper.decorators.virtual_method
    def get_selection(self):
        raise NotImplementedError

    @get_selection.override("designer")
    def get_selection(self):
        import sd
        output = []
        if(self.wraps):
            uimgr = sd.getContext().getSDApplication().getQtForPythonUIMgr()
            for i in uimgr.getCurrentGraphSelection():
                output.append(juniper.dcc.types.scene_graph.node.Node(i))
        return output
