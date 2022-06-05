import os
import pymxs

import juniper
import pymxs.juniper.sdk as max_sdk
import juniper.utilities.pathing as pathing_utils


def path():
    """
    :return <str:path> The path to the current Max file - None if it doesn't exist
    """
    output = pathing_utils.sanitize_path(
        os.path.join(pymxs.runtime.maxFilePath, pymxs.runtime.maxFileName)
    )
    if(os.path.isfile(output)):
        return output
    return None


def name():
    """
    :return <str:name> The name of the scene (minus the .max suffix) - None if the file is not saved
    """
    output = pymxs.runtime.maxFileName
    if(output not in ("", None)):
        return output.split(".")[0]
    return None


def clone(nodes, deep_clone=True, instance=False, copy=True, reference=False, select_copies=False):
    """Clones an object or an array of objects
    :param <[node]|node:nodes> An array of nodes, or a single node
    """
    copies = []

    mode = pymxs.runtime.copy
    if(reference):
        mode = pymxs.runtime.reference
    elif(instance):
        mode = pymxs.runtime.instance

    if(type(nodes) not in (tuple, list)):
        nodes = [nodes]

    for obj in nodes:
        copied_object = None
        try:
            copied_object = mode(obj)
            copies.append(copied_object)

            if(deep_clone):
                # copy all user properties from the base object to the new one
                pymxs.runtime.setUserPropBuffer(copied_object, pymxs.runtime.getUserPropBuffer(obj))

                # copy to selection sets
                for i in range(pymxs.runtime.selectionSets.count):
                    current_selection_set = pymxs.runtime.selectionSets[i]
                    if(pymxs.runtime.findItem(current_selection_set, obj) != 0):
                        # have to duplicate and set in place to a max array in order to append
                        current_selection_set_objects = pymxs.runtime.array()
                        for o in current_selection_set:
                            pymxs.runtime.append(current_selection_set_objects, o)
                        pymxs.runtime.append(current_selection_set_objects, copied_object)
                        pymxs.runtime.selectionSets[current_selection_set.name] = current_selection_set_objects

                # copy general properties
                copied_object.parent = obj.parent
                copied_object.boxMode = obj.boxMode
                copied_object.isHidden = obj.isHidden
                copied_object.isFrozen = obj.isFrozen
                copied_object.allEdges = obj.allEdges
                copied_object.material = obj.material
                copied_object.wireColor = obj.wireColor
                copied_object.showVertexColors = obj.showVertexColors
                copied_object.showFrozenInGray = obj.showFrozenInGray
        except Exception:
            if(copied_object):
                pymxs.runtime.delete(copied_object)
            juniper.log.error(f"Failed to copy node {obj.name}")

    if(select_copies):
        pymxs.runtime.select(copies)

    return copies


def pick_node(position, get_inode=False):
    """Picks a node in the viewport from a viewport position
    :param <[float]:position> Fractional [0..1] position in the viewport to pick
    :return <INode:node> Picked node - None if nothing was picked
    """
    instance = max_sdk.GetGlobalInterface()
    pos_point2 = instance.Point2.Create(position[0], position[1])
    i_point2 = instance.IPoint2NS.Create(int(pos_point2.X), int(pos_point2.Y))

    interface = instance.UtilGetCOREInterface
    view_exp = interface.ActiveViewExp
    view_exp.ClearHitList()
    view_handle = view_exp.HWnd
    node = interface.PickNode(view_handle, i_point2, filt=None)

    if(not get_inode):
        if(node):
            return pymxs.runtime.maxOps.getNodeByHandle(node.Handle)
        return None
    return node


def hit_test_face(inode, position):
    """Takes an input node and viewport position and returns the face ID that is hit
    :param <INode:inode> The inode to work on
    :param <[int]:position> Screen position to test at
    :return <int:face_id> ID of the face hit, None if nothing was hit
    """
    instance = max_sdk.GetGlobalInterface()
    interface = max_sdk.GetCOREInterface()

    pos = instance.IPoint2NS.Create(int(position[0]), int(position[1]))

    # graphics window
    view_exp = max_sdk.GetActiveViewExp()
    graphics_window = view_exp.Gw

    hit_region = instance.HitRegion.Create()
    instance.MakeHitRegion(hit_region, 0x0001, 1, 4, pos)  # 0x0001 = POINT_RGN
    graphics_window.SetHitRegion(hit_region)

    tx = inode.GetObjectTM(interface.Time, valid=None)
    graphics_window.Transform = tx
    graphics_window.ClearHitCode()

    # see https://help.autodesk.com/view/MAXDEV/2022/ENU/?guid=Max_Developer_Help_cpp_ref_class_hit_list_wrapper_html
    object_wrapper = instance.ObjectWrapper.Create()
    object_wrapper.Init(
        0,
        inode.EvalWorldState(max_sdk.GetTime(), evalHidden=True),
        copy=False,
        enable=0x7,  # default
        nativeType=2  # polyObject
    )

    # see https://help.autodesk.com/view/3DSMAX/2016/ENU/?guid=__cpp_ref_class_hit_list_wrapper_html
    hit_list_wrapper = instance.HitListWrapper.Create()
    hit_list_wrapper.Init(2)
    result = object_wrapper.SubObjectHitTest(
        2,  # SEL_FACE
        graphics_window,
        graphics_window.Material,
        hit_region,
        1 << 25,  # SUBHIT_MNFACES
        hit_list_wrapper,
        numMat=1,
        mat=None
    )

    if(result):
        # get the closest one
        hit_list_wrapper.GoToFirst
        closest = hit_list_wrapper.Index
        min_dist = hit_list_wrapper.Dist

        while(1):
            if(min_dist > hit_list_wrapper.Dist):
                min_dist = hit_list_wrapper.Dist
                closest = hit_list_wrapper.Index
            if(not hit_list_wrapper.GoToNext):
                break
        return closest + 1
    return None
