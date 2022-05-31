"""
Library for texture based functionality in Unreal
"""
import os
import unreal


def import_texture(real_path, upath, save=False, replace_existing=True, replace_existing_settings=False, texture_compression_method=None, srgb=None):
    """
    Import a texture into unreal given its real path and a target path.
    :param <str:real_path> The absolute path to the texture to import
    :param <str:upath> The content browser relative path for the asset (Ie, "/Game/Folder/Example")
    :param [<bool:save>] Should the asset be saved?
    :param [<bool:replace_existing>] Should this replace any existing asset?
    :param [<TextureCompressionMethod:texture_compression_method>] The unreal texture compression method to use
    :param [<bool:srgb>] Should SRGB be used on the texture? If None the unreal default will be used.
    :return <UTexture:texture> The texture asset object if imported - else None
    """
    output = None

    if(os.path.isfile(real_path)):
        import_task = unreal.AssetImportTask()
        import_task.set_editor_property("filename", real_path)
        import_task.set_editor_property("destination_path", os.path.dirname(upath))
        import_task.set_editor_property("save", save)
        import_task.set_editor_property("replace_existing", replace_existing)
        import_task.set_editor_property("replace_existing_settings", replace_existing_settings)
        import_task.set_editor_property("automated", True)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])

        for i in import_task.imported_object_paths:
            asset = unreal.AssetData(object_path=i)
            output = unreal.AssetRegistryHelpers.get_asset(asset)
            if(texture_compression_method):
                output.compression_settings = texture_compression_method
            if(srgb is not None):
                output.srgb = srgb
            if(save):
                unreal.EditorAssetLibrary.save_loaded_asset(output, only_if_is_dirty=False)

    return output
