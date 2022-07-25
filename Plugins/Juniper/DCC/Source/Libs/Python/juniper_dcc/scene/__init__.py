"""
Scene based functions
"""
import os

import juniper.decorators
from .scene_wrapper import SceneWrapper
from .object_wrapper import ObjectWrapper
import juniper.utilities.pathing
import juniper.utilities.array


# --------------------------------------------------------------

@juniper.decorators.virtual_method
def get_current():
    """
    Gets a reference to the object for the current scene wrapped in a juniper SceneWrapper object
    :return <SceneWrapper:scene> The current scene object
    """
    raise NotImplementedError


@get_current.override("designer")
def _get_current():
    import sd.juniper.graph
    current_graph = sd.juniper.graph.current()
    if(current_graph):
        return SceneWrapper(current_graph)
    return None


@get_current.override("painter")
def _get_current():
    import substance_painter.project
    # painter does not have a scene object type
    # so just store the file name so we have something to compare against
    # when needed, and for caching purposes
    path = substance_painter.project.file_path().replace("/", "\\")
    return SceneWrapper(path)


@get_current.override("max")
def _get_current():
    import pymxs
    import pymxs.juniper.scene
    current_scene_path = pymxs.juniper.scene.path()
    # max does not have a scene object type
    # so just store the file name so we have something to compare against
    # if it is unsaved then it will wrap None, which should still work
    # just without any file IO logic
    return SceneWrapper(current_scene_path)


@get_current.override("blender")
def _get_current():
    import bpy
    path = bpy.data.filepath
    if(path and os.path.isfile(path)):
        return SceneWrapper(path)
    return None

# --------------------------------------------------------------


@juniper.decorators.virtual_method
def load(scene_path):
    """
    Loads a scene from a given file path
    :param <str:scene_path> The absolute file path of the scene
    :return <SceneWrapper:scene> The loaded scene object
    """
    raise NotImplementedError


@load.override("designer")
def _load(scene_path):
    import sd.juniper.instance
    package_manager = sd.juniper.instance.package_manager

    if((os.path.isfile(scene_path)) and (scene_path.endswith(".sbs"))):
        package_manager.loadUserPackage(scene_path.replace("\\", "/"), True, True)
        return get_current()
    return None


@load.override("painter")
def _load(scene_path, save_scene=True):
    import substance_painter.project
    if(substance_painter.project.is_open()):
        get_current().close(not save_scene)

    if(os.path.isfile(scene_path)):
        substance_painter.project.open(scene_path)
        return get_current()
    return None


# --------------------------------------------------------------


@juniper.decorators.virtual_method
def get_selection():
    """
    Gets a list containing the currently selected objects in the current scene
    :return <[ObjectWrapper]:selection> Selected objects
    """
    raise NotImplementedError


@get_selection.override("max")
def _get_selection():
    import pymxs
    output = []
    for i in pymxs.runtime.selection:
        node = ObjectWrapper(i)
        output.append(node)
    return output


@get_selection.override("unreal")
def _get_selection():
    import unreal
    output = []
    for i in unreal.EditorLevelLibrary.get_selected_level_actors():
        node = ObjectWrapper(i)
        output.append(node)
    return output

# --------------------------------------------------------------


@juniper.decorators.virtual_method
def clear_selection():
    """
    Clears the current selection
    """
    raise NotImplementedError


@clear_selection.override("max")
def _clear_selection():
    import pymxs
    pymxs.runtime.clearSelection()

# --------------------------------------------------------------


@juniper.decorators.virtual_method
def set_selection(selection=None):
    """
    Sets the selection to the input array
    :param <[ObjectWrapper]:selection> The new selection array
    """
    clear_selection()
    if(selection):
        for i in selection:
            i.select()

# --------------------------------------------------------------


@juniper.decorators.virtual_method
def select(*args):
    """
    Selects the input object_name - this does not remove from current selection
    """
    for i in juniper.utilities.array.consolidate_array(args):
        i.select()

# --------------------------------------------------------------


@juniper.decorators.virtual_method
def get_objects():
    """
    Gets a list containing all objects in the current scene
    :return <[ObjectWrapper]:objects> All objects in the current scene
    """
    raise NotImplementedError


@get_objects.override("max")
def _get_objects():
    import pymxs
    output = []
    for i in pymxs.runtime.objects:
        node = ObjectWrapper(i)
        output.append(node)
    return output


@get_objects.override("unreal")
def _get_objects():
    import unreal
    output = []
    for i in unreal.EditorLevelLibrary.get_all_level_actors():
        node = ObjectWrapper(i)
        output.append(node)
    return output


@juniper.decorators.virtual_method
def find_object(object_name):
    """
    Searches the current scene for an object given a target name
    :param <str:object_name> The name of the node to find
    :return <NodeWrapper:node> The node if found - else none
    """
    raise NotImplementedError


@find_object.override("max")
def _find_object(object_name, ignore_case=False):
    import pymxs
    possible_node = pymxs.runtime.getNodeByName(object_name, ignoreCase=ignore_case)
    if(possible_node):
        return ObjectWrapper(possible_node)
    return None

# --------------------------------------------------------------


def unique_name(name, numerical=True):
    """
    Generates a new unique name from an input with respect to the current scene objects
    :param <str:name> The target name to generate
    :param [<bool:numerical>] If True then numerical suffixes will be used - if False Alphabetical suffixes will be used
    :return <str:name> The newly generated name
    """
    if(find_object(name)):
        if(numerical):
            for i in range(1, 99):
                suffix = str(i) if i >= 10 else f"0{i}"
                possible_name = f"{name}_{suffix}"
                if(not find_object(possible_name)):
                    return possible_name
        else:
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            for i in alphabet:
                possible_name = f"{name}_{i}"
                if(not find_object(possible_name)):
                    return possible_name
    else:
        return name
