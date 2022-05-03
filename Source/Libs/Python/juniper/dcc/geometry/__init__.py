"""
Wrapper class for a geometry type.

TODO~:   Implementation, this will be an extensive asset implementation due to the different native objects
        that can be wrapped, and the fact multiple can be per-program.

        Some of these types can also only be wrapped for helper reasons, Ie Painter, which should only have
        support for exporting the FXB from the scene

TODO~:
    - run_import(ue4)
    - fbx interface
    - get materials on object?
    - material metadata exporting?
"""
import os

import juniper.dcc.scene
import juniper.dcc.scene.selection_set_wrapper
import juniper.dcc.scene.object_wrapper
import juniper.decorators
import juniper.framework.types.asset_interface
import juniper.framework.wrappers.type_wrapper
import juniper.utilities.string as string_utils


class GeometryWrapperManager(juniper.framework.wrappers.type_wrapper.TypeWrapperManager):
    pass


class GeometryWrapper(juniper.framework.wrappers.type_wrapper.TypeWrapper):
    __manager__ = GeometryWrapperManager

    def __init__(self, native_object, asset_data_path=None):
        """
        Wrapper class for a Texture type object
        Multiple types can be used for wrapping depending on the implementation, for example:
        :wraps <max:SelectionSetWrapper> Used for treating the contents as a single entity
        :wraps <max:NodeWrapper> Used for treating a single node as an entity
        :wraps <max:LayerWrapper> used for treating a layer as an entity (TODO~: Implement LayerWrapper)
        :wraps <designer:FBXResource> Used to treat an imported FBX as an entity
        :wraps <painter:SceneWrapper> Treats the mesh in the scene as an entity
        :wraps <ue4:UStaticMesh> Treats the static mesh actor as an entity
        :param <NativeType:native_object> The native object to wrap
        :param [<str:asset_data_path>] Optional path to a .geometry json file
        """
        super().__init__(native_object)
        self.load_asset_interface(asset_data_path)

    def load_asset_interface(self, asset_data_path):
        """
        Loads in the asset data directly from a path
        :param [<str:asset_data_path>] The path to the asset file
        """
        if(asset_data_path):
            self.asset_interface = juniper.framework.types.asset_interface.AssetInterface(
                asset_data_path,
                create_if_invalid=True
            )
        else:
            self.asset_interface = juniper.framework.types.asset_interface.AssetInterface("", create_if_invalid=False)

    # ----------------------------------------------------------------

    @property
    def name(self):
        """
        :return <str:name> The name of this geometry (Ie, "SM_SomeGeo_01")
        """
        output = self.get_name()
        if(output is not None):
            if(not output.lower().startswith("sm_")):
                output = "SM_" + output
        return self.__validate_name(output)

    def __validate_name(self, input_):
        output = input_
        if("{package}" in output):
            current_scene = juniper.dcc.scene.get_current()
            if(current_scene):
                # TODO~: Export validation - we should not be able to export in this situation without a saved file
                current_scene_name = current_scene.name
                output = output.replace("{package}", current_scene_name)
        return output

    @property
    def name_only(self):
        """
        :return <str:name> The name of this geometry minus the "SM_" prefix
        """
        return string_utils.remove_prefix(self.name, "SM_")

    @juniper.decorators.virtual_method
    def get_name(self):
        raise NotImplementedError

    @get_name.override("max")
    def _get_name(self):
        output = None
        try:
            output = self.native_object.name
        except Exception:
            # if we've hit a non supported wrap type
            # TODO~: LayerWrapper ?
            raise NotImplementedError
        return output

    # ----------------------------------------------------------------

    @property
    def path(self):
        """
        :return <str:path> The path to this geometry asset
        """
        return self.get_path()

    @juniper.decorators.virtual_method
    def get_path(self):
        raise NotImplementedError

    @get_path.override("max")
    def _get_path(self):
        import juniper.dcc.scene
        current_scene = juniper.dcc.scene.get_current()
        if(current_scene):
            return current_scene.path
        return None

    # ----------------------------------------------------------------

    def export(self, output_dir, meshes_subdir=None, export_asset_data=False, filename_override=None):
        """
        Exports this geometry from the current host application
        :param <str:output_dir> The directory to output the geometry + data to
        :param [<str:meshes_subdir>] Optional subdirectory for exporting the .FBX files to
        :param [<bool:export_asset_data>] Should a ".geometry" metadata file be exported to the output directory?
        :param [<str:filename_override>] Optional override for the filename - useful when the parent native objects name needs altering before exporting.
        """
        self.asset_interface.set_metadata_key("#export:output_dir", output_dir)
        self.asset_interface.set_metadata_key("#export:meshes_output_dir", os.path.join(output_dir, meshes_subdir) if meshes_subdir else output_dir)

        if(filename_override):
            self.asset_interface.set_metadata_key("#export:filename_override", filename_override)

        success = self.__export()

        if(success and export_asset_data):
            self.asset_interface.save()

        return success

    @juniper.decorators.virtual_method
    def __export(self):
        """
        run the base export logic
        :return <bool:success> True if the geometry was exported successfully - else False
        """
        raise NotImplementedError

    @__export.override("max")
    def __export(self):
        import juniper.framework.programs.max.export as max_export

        success = False

        export_output_dir = self.asset_interface.get_metadata_key("#export:meshes_output_dir")
        export_filename_override = self.asset_interface.get_metadata_key("#export:filename_override")
        export_output_path = os.path.join(export_output_dir, export_filename_override or self.name)

        # Export: From SceneWrapper
        if(isinstance(self.native_object, juniper.dcc.scene.SceneWrapper)):
            success = max_export.export_nodes(
                [x.native_object for x in self.native_object.objects],
                export_output_path
            )

        # Export: From SelectionSetWrapper
        elif(isinstance(self.native_object, juniper.dcc.scene.selection_set_wrapper.SelectionSetWrapper)):
            success = max_export.export_nodes(
                [x.native_object for x in self.native_object.objects],
                export_output_path
            )

        # Export: From ObjectWrapper
        elif(isinstance(self.native_object, juniper.dcc.scene.object_wrapper.ObjectWrapper)):
            success = max_export.export_nodes([self.native_object])

        else:
            raise NotImplementedError

        return success
