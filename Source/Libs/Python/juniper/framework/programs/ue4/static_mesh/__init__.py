"""
Library for static mesh based functionality in unreal
"""
import os
import unreal


def import_static_mesh(
    real_path,
    upath,
    import_textures=False,
    import_materials=False,
    reset_to_fbx_on_material_conflicts=True,
    combine_meshes=True,
    reorder_material_to_fbx_order=True,
    save=False,
    replace_existing=True
):
    """
    Imports a static mesh / fbx into unreal given its real path and target path
    :param <str:real_path> The absolute path to the texture to import
    :param <str:upath> The content browser relative path for this asset (Ie, "/Game/Folder/Example")
    :param [<bool:import_textures>] Should textures be imported with the FBX?
    :param [<bool:import_materials>] Should materials be imported with the FBX?
    :param [<bool:reset_to_fbx_on_material_conflicts>] Should the materials be reset if conflicts are found?
    :param [<bool:combine_meshes>] Should meshes be combined?
    :param [<bool:reorder_material_to_fbx_order>] Should material indices be reordered to the FBX order?
    :param [<bool:save>] Should the asset be saved?
    :param [<bool:replace_existing>] Should this asset replace existing assets?
    :return <UStaticMesh:mesh> The imported static mesh object if imported - else None
    """
    output = None

    if(os.path.isfile(real_path)):
        fbx_options = unreal.FbxImportUI()
        fbx_options.set_editor_property("import_mesh", True)
        fbx_options.set_editor_property("import_as_skeletal", False)
        fbx_options.import_as_skeletal = False
        fbx_options.set_editor_property("import_textures", import_textures)
        fbx_options.set_editor_property("import_materials", import_materials)
        fbx_options.set_editor_property("import_rigid_mesh", False)
        fbx_options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
        fbx_options.set_editor_property("original_import_type", unreal.FBXImportType.FBXIT_STATIC_MESH)
        fbx_options.set_editor_property("physics_asset", None)
        fbx_options.set_editor_property("reset_to_fbx_on_material_conflict", reset_to_fbx_on_material_conflicts)
        fbx_options.static_mesh_import_data.set_editor_property("combine_meshes", combine_meshes)
        fbx_options.static_mesh_import_data.set_editor_property("reorder_material_to_fbx_order", reorder_material_to_fbx_order)

        task = unreal.AssetImportTask()
        task.set_editor_property("automated", True)
        task.set_editor_property("filename", real_path)
        task.set_editor_property("destination_path", os.path.dirname(upath))
        task.set_editor_property("replace_existing", replace_existing)
        task.set_editor_property("save", save)
        task.set_editor_property("options", fbx_options)

        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

        for i in task.imported_object_paths:
            asset = unreal.AssetData(object_path=i)
            output = unreal.AssetRegistryHelpers.get_asset(asset)
            if(save):
                unreal.EditorAssetLibrary.save_loaded_asset(output, only_if_is_dirty=False)

    return output
