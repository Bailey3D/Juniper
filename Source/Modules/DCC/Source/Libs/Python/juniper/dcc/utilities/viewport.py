"""
Utility functions for interacting with the viewport in the current DCC application
"""
import juniper.dcc.types.node
import juniper.dcc.types.scene
import juniper.decorators
import juniper.utilities.array


@juniper.decorators.virtual_method
def focus(*args):
    """
    Focuses a selection of nodes in the viewport
    :param <[Node]:*args> The nodes to focus - a single object, array of objects, or *args of objects
    """
    raise NotImplementedError


@focus.override("max")
def focus(*args):
    import pymxs

    if(args):
        scene = juniper.dcc.types.scene.Scene()
        selection_cache = scene.selection
        for i in juniper.utilities.array.consolidate_arrays(args):
            i.select()
        pymxs.runtime.actionMan.executeAction(0, "310")  # Tools: Zoom Extents Selected
        pymxs.runtime.redrawViews()
        scene.selection = selection_cache
    else:
        pymxs.runtime.actionMan.executeAction(0, "310")  # Tools: Zoom Extents Selected
        pymxs.runtime.redrawViews()
