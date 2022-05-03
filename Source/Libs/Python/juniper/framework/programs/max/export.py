"""
Export based wrapper functions
"""
import os

import pymxs


def export_nodes(
    nodes,
    file_path,
    export_animation=False,
    convert_unit="cm",
    smoothing_groups=True,
    smooth_mesh_export=True,
    show_warnings=False,
    tangent_space_export=True
):
    """
    Exports a series of nodes as an FBX to the given path
    :param <[Node]:nodes> The Max nodes to export
    :param <str:file_path> The path to export the FBX to
    :param [<bool:export_animation>] Should animation be exported?
    :param [<str:convert_unit>] The unit to convert to - defaults to "cm"
    :param [<bool:smoothing_groups>] Should the geometry be exported with smoothing groups?
    :param [<bool:smooth_mesh_export>] Should smooth mesh export be set?
    :param [<bool:show_warnings>] Should warnings be shown?
    :param [<bool:tangent_space_export>] Should tangent space export be used?
    :return <bool:success> True if the geometry was exported - else False
    """
    success = False

    selection_cache = [x for x in pymxs.runtime.selection]

    with pymxs.undo(False):
        if(not os.path.isdir(os.path.dirname(file_path))):
            os.makedirs(os.path.dirname(file_path))

        try:
            merged_geometry = pymxs.runtime.editable_mesh()
            pymxs.runtime.convertToPoly(merged_geometry)

            for o in nodes:
                copy = pymxs.runtime.copy(o)
                pymxs.runtime.convertToPoly(copy)
                pymxs.runtime.polyOp.attach(merged_geometry, copy)

            if(not os.path.isdir(os.path.dirname(file_path))):
                os.makedirs(os.path.dirname(file_path))

            pymxs.runtime.select(merged_geometry)
            pymxs.runtime.FBXExporterSetParam("ResetExport")
            pymxs.runtime.FBXExporterSetParam("Animation", export_animation)
            pymxs.runtime.FBXExporterSetParam("ConvertUnit", convert_unit)
            pymxs.runtime.FBXExporterSetParam("SmoothingGroups", smoothing_groups)
            pymxs.runtime.FBXExporterSetParam("SmoothMeshExport", smooth_mesh_export)
            pymxs.runtime.FBXExporterSetParam("ShowWarnings", show_warnings)
            pymxs.runtime.FBXExporterSetParam("TangentSpaceExport", tangent_space_export)
            pymxs.runtime.exportFile(file_path, pymxs.runtime.name("noPrompt"), selectedOnly=True, using="FBXEXP")

            success = True

        except Exception as e:
            if(show_warnings):
                print(str(e))
            success = False

        finally:
            pymxs.runtime.delete(merged_geometry)

    pymxs.runtime.select(selection_cache)

    return success
