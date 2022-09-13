"""
Viewport based functions
"""
import jdcc.scene
import juniper.decorators
import juniper.utilities.array


# -----------------------------------------------------------

@juniper.decorators.virtual_method
def __focus_selection():
    """
    Focus the currently selected objects
    """
    raise NotImplementedError


@__focus_selection.override("max")
def __focus_selection():
    import pymxs
    pymxs.runtime.actionMan.executeAction(0, "310")  # Tools: Zoom Extents Selected
    pymxs.runtime.redrawViews()

# -----------------------------------------------------------


@juniper.decorators.virtual_method
def focus(*args):
    """
    Focus an object / objects in the viewport
    :param <[ObjectWrapper]:*args> The objects to focus - either a single object array of objects, or *args of objects
    """
    if(len(args)):
        selection_cache = jdcc.scene.get_selection()
        for i in juniper.utilities.array.consolidate_array(args):
            i.select()

        __focus_selection()
        jdcc.scene.set_selection(selection_cache)
    else:
        __focus_selection()
