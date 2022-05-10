import os

import juniper
import juniper.dcc.scene
import juniper.decorators
import juniper.framework.programs.ue4
import juniper.framework.types.asset_interface
import juniper.framework.wrappers.type_wrapper
import juniper.utilities.string as string_utils


class MaterialWrapperManager(juniper.framework.wrappers.type_wrapper.TypeWrapperManager):
    pass


class MaterialWrapper(juniper.framework.wrappers.type_wrapper.TypeWrapper):
    __manager__ = MaterialWrapperManager

    def __init__(self, native_object, asset_data_path=None):
        """
        Wrapper class for a Material object
        :wraps <painter:TextureSetObject>
        :wraps <designer:Graph>
        :param <NativeType:native_object> The native object to wrap
        :param [<str:asset_data_path>] Optional path to a .material json file
        """
        super().__init__(native_object)
        self.load_asset_interface(asset_data_path)

    def load_asset_interface(self, asset_data_path):
        """
        Loads in the asset data directly from a path
        Useful as sometimes information in the material is needed before we can calculate the path to the asset
        :param [<str:asset_data_path>] The path to the asset file
        """
        if(asset_data_path):
            self.asset_interface = juniper.framework.types.asset_interface.AssetInterface(
                asset_data_path,
                create_if_invalid=True
            )
        else:
            self.asset_interface = juniper.framework.types.asset_interface.AssetInterface("", create_if_invalid=False)

    # ---------------------------------------------------

    @property
    def name(self):
        """
        :return <str:name> The name of this material (Ie, "M_Terrain_01")
        """
        output = self.get_name()
        if(not output.lower().startswith("m_")):
            output = "M_" + output
        return output

    @property
    def name_only(self):
        """
        :return <str:name> The name of this material minus the "M_" prefix
        """
        return string_utils.remove_prefix(self.name, "M_")

    @juniper.decorators.virtual_method
    def get_name(self):
        raise NotImplementedError

    @get_name.override("designer")
    def _get_name(self):
        import juniper_designer.package
        output = self.native_object.getIdentifier()

        if("{package}" in output):
            # It would be nice to follow the same $(key) format as substance internally
            # but it doesn't allow for the characters "$" "(" and ")" in graph names.
            # We'll just the "{key}" format like python fstrings instead
            package_name = juniper_designer.package.get_name(
                package=self.native_object.getPackage()
            )
            output = output.replace("{package}", package_name)

        return output

    @get_name.override("painter")
    def _get_name(self):
        output = str(self.native_object)
        package_name = juniper.dcc.scene.get_current().name
        output = output.replace("{package}", package_name)
        return output

    # ---------------------------------------------------

    @property
    def base_name(self):
        """
        :return <str:name> The base name of this material minus any types / variants (Ie, `M_Example_01_a` -> `M_Example`)
        """
        output = self.get_base_name()
        if(not output.lower().startswith("m_")):
            output = "M_" + output
        return output

    @property
    def base_name_only(self):
        """
        :return <str:name> The base name of this material minus the "M_" prefix
        """
        return string_utils.remove_prefix(self.base_name, "M_")

    @juniper.decorators.virtual_method
    def get_base_name(self):
        raise NotImplementedError

    @get_base_name.override("painter")
    def _get_base_name(self):
        return juniper.dcc.scene.get_current().name

    @get_base_name.override("designer")
    def _get_base_name(self):
        return juniper_designer.package.get_name(
            package=self.native_object.getPackage()
        )

    # ---------------------------------------------------

    @property
    def path(self):
        """
        :return <str:path> The path to this material asset
        """
        return self.get_path()

    @juniper.decorators.virtual_method
    def get_path(self):
        raise NotImplementedError

    @get_path.override("designer")
    def _get_path(self):
        return self.native_object.getPackage().getFilePath().replace("/", "\\")

    @get_path.override("painter")
    def _get_path(self):
        return juniper.dcc.scene.get_current().path

    # ---------------------------------------------------

    def __validate_exported_texture(self, texture_type, texture_path):
        """
        Runs some extra validation on an exported texture, including filename validation
        :param <str:texture_type> The texture type (Ie, "S", "N", "DA")
        :param <str:texture_path> Absolute path to the texture
        :return <str:validated_path> The path after processing
        """
        # replace certain keywords from material names programatically 
        # (Ie, `{package}` -> the current scene name)
        # currently only supports `{package}` keyword
        old_fp = texture_path.replace("/", "\\")
        new_fp = old_fp.replace("{package}", juniper.dcc.scene.get_current().name)
        file_function = os.rename if not os.path.isfile(new_fp) else os.replace
        file_function(old_fp, new_fp)

        # make relative to target directory if set ..
        relative_to = self.asset_interface.get_metadata_key("#export:relative_to")
        if(relative_to):
            relative_exported_texture_path = string_utils.remove_prefix(new_fp.lower(), relative_to.lower())
            relative_exported_texture_path = relative_exported_texture_path.lstrip("\\")
        else:
            relative_exported_texture_path = new_fp

        # make relative to the current unreal project if it is under it and a parent was not set ..
        relative_exported_texture_path = string_utils.remove_prefix(
            relative_exported_texture_path,
            os.path.join(juniper.framework.programs.ue4.unreal_project_dir(), "content")
        )
        relative_exported_texture_path = relative_exported_texture_path.lstrip("\\")

        self.asset_interface.set_key(texture_type, relative_exported_texture_path, "textures")
        return relative_exported_texture_path

    def export(self, output_dir, textures_subdir=None, relative_to=None, export_metadata=False):
        """
        Export this material asset from the current host application
        :param <str:output_dir> The directory to output the material + data to
        :param [<str:textures_subdir>] Optional subdirectory to export textures to
        :param [<str:relative_to>] Optional path to make the exported textures relative to - to avoid hardcoded paths
        :param [<bool:export_metadata>] Should a `.material` metadata file be exported to the output directory?
        :return <bool:success> True if the material was exported successfully - else False
        """
        self.asset_interface.set_metadata_key("#export:relative_to", relative_to)
        self.asset_interface.set_metadata_key("#export:textures_subdir", textures_subdir)
        self.asset_interface.set_metadata_key("#export:output_dir", output_dir)
        self.asset_interface.set_metadata_key("#export:textures_output_dir", os.path.join(output_dir, textures_subdir) if textures_subdir else output_dir)

        success = self.__export()

        if(success and export_metadata):
            self.asset_interface.set_metadata_key("base_name", self.base_name)
            self.asset_interface.save()

        return success

    @juniper.decorators.virtual_method
    def __export(self):
        """
        Run the base export logic
        :return <bool:success> True if the material was exported successfully - else False
        """
        raise NotImplementedError

    @__export.override("painter")
    def __export(self):
        export_output_dir = self.asset_interface.get_metadata_key("#export:output_dir")
        export_preset_name = self.asset_interface.get_metadata_key("export:preset", subgroup="painter")
        if(export_output_dir and export_preset_name):
            import juniper.framework.programs.painter.shelf
            import juniper.framework.programs.painter.export_config

            export_preset_resource = juniper.framework.programs.painter.shelf.find_resource(export_preset_name, max_retries=4)
            if(export_preset_resource):
                # TODO~: Should the exportParameters be stored in the .material file?
                # will still need a way to set this from within Painter though
                export_config = juniper.framework.programs.painter.export_config.ExportConfig(
                    export_preset_resource.url(),
                    self.asset_interface.get_metadata_key("#export:textures_output_dir"),
                    texture_sets=str(self.native_object)
                )
                export_results = export_config.export_project_textures()

                for k, v in export_results.textures.items():
                    for fp in v:
                        # TODO~: This is just the texture suffix, the metadata needs the actual parameter name
                        texture_suffix = fp.split("_")[-1].split(".")[0]
                        self.__validate_exported_texture(texture_suffix, fp)
                return True
        return False

    @__export.override("designer")
    def __export(self):
        import juniper_designer.graph

        if(self.asset_interface.get_metadata_key("#export:output_dir")):
            export_data = juniper_designer.graph.export_textures(
                self.native_object, material_name=self.name_only, export_directory=self.asset_interface.get_metadata_key("#export:textures_output_dir")
            )
            if(export_data):
                for k, v in export_data.items():
                    self.__validate_exported_texture(k, v)
                return True
        return False
