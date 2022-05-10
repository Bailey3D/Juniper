import os
import sd
from sd.api.sdproperty import SDPropertyCategory


context = sd.getContext()
app = context.getSDApplication()
package_manager = app.getPackageMgr()
ui_manager = app.getQtForPythonUIMgr()


def current():
    """Attempt to find the currently opened designer graph
    :return <sdsbsgraph:graph> The currently opened graph - None no graph is open
    """
    return ui_manager.getCurrentGraph()


def _ensure_graph(graph):
    """Ensures that we have a package to work on. If the input is None then we default to the current package
    :param <sdsbsgraph:package> Target graph - if None we will return the currently opened graph
    :return <sdsbsgraph:output> Either the input graph or currently opened one
    """
    if(graph is None):
        return current()
    return graph


def graph_selection():
    """Returns the currently selected nodes in the opened graph
    :return <sdarray:nodes> Nodes if there is a valid selection, else an empty array
    """
    return ui_manager.getCurrentGraphSelection()


def graph_name(target=None):
    """Get the name of a graph
    :param <sdsbsgraph:target> Target graph, if None then will default to the currently opened graph
    :return <str:name> Name of the currently opened graph
    """
    if(target is None):
        target = current()
    if(target is not None):
        return target.getPropertyValueFromId("identifier", SDPropertyCategory.Annotation).get()
    return ""


def export_textures(graph, material_name, export_directory):
    """
    :param <sdsbsgraph:graph> The graph to export
    :param <str:material_name> The name of the material (Minus any "M_")
    :param <str:export_directory> The directory to export these textures to
    :return <dict:metadata> Metadata on the exported textures - key = texture type identifier (Ie, "S", "N"), value = export path - None if the export fails
    """
    export_data = {}

    try:
        graph.compute()

        for node in graph.getOutputNodes():
            node_definition = node.getDefinition()
            node_outputs = node_definition.getProperties(
                sd.api.sdproperty.SDPropertyCategory.Output
            )
            node_texture = None

            for node_output in node_outputs:
                prop_value = node.getPropertyValue(node_output)
                prop_texture = prop_value.get()
                # node_label_props = node.getProperties(sd.api.sdproperty.SDPropertyCategory.Output)
                # node_label = str(node_label_props[0].getLabel())
                if(prop_texture):
                    node_texture = prop_texture
                    break
            if(node_texture):
                texture_type = node.getAnnotationPropertyValueFromId("identifier").get()
                texture_name = f"T_{material_name}_{texture_type}"
                texture_export_path = os.path.join(export_directory, texture_name + ".tga")
                node_texture.save(texture_export_path)
                export_data[texture_type] = texture_export_path
    except Exception:
        export_data = None

    return export_data
