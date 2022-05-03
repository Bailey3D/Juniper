"""
Export based functions
"""
import substance_painter.export


class ExportConfig(object):
    def __init__(
        self,
        export_preset,
        export_path,
        export_shader_params=False,
        file_format="tga",
        bit_depth=8,
        dithering=True,
        padding_algorithm="infinite",
        texture_sets=[]
    ):
        """
        Wrapper for the dict based export configurations required to export from Painter
        :param <str:export_preset> Resource URL to an export preset (Ie, `PBR Metallic Roughness`)
        :param <str:export_path> The directory to export textures to
        :param [<bool:export_shader_params>] Should shader parameters be exported to a .json file?
        :param [<str:file_format>] The file format of exported textures - defaults to TGA
        :param [<int:bit_depth>] Bith depth of the exported textures - defaults to 8
        :param [<bool:dithering>] Should dithering be used to reduce banding?
        :param <str:padding_algorithm> The padding algorithm to use - defaults to "infinite"
        """
        self.export_shader_params = export_shader_params
        self.export_preset = export_preset
        self.export_path = export_path
        self.file_format = file_format
        self.bit_depth = bit_depth
        self.dithering = dithering
        self.padding_algorithm = padding_algorithm
        self.export_texture_sets = [texture_sets] if isinstance(texture_sets, str) else texture_sets

    def add_texture_set(self, texture_set_name):
        """
        Adds a texture set to the list of texture sets to export
        :param <str:texture_set_name> The name of the texture set to add
        """
        if(texture_set_name not in self.export_texture_sets):
            self.export_texture_sets.append(texture_set_name)

    def to_json(self):
        """
        Converts this object to a dict as used by the inbuilt painter methods
        :return <dict:output> Output dict as required by painter
        """
        output = {}
        output["exportShaderParams"] = self.export_shader_params
        output["defaultExportPreset"] = self.export_preset
        output["exportPath"] = self.export_path

        output["exportList"] = []
        for i in self.export_texture_sets:
            output["exportList"].append({"rootPath": i})

        output["exportParameters"] = [{
            "parameters": {
                "fileFormat": self.file_format,
                "bitDepth": str(self.bit_depth),
                "dithering": self.dithering,
                "paddingAlgorithm": self.padding_algorithm
            }
        }]

        return output

    def export_project_textures(self):
        """
        Wrapper for `substance_painter.export.export_project_textures`
        :return <TextureExportResult:result> Painter export result data
        """
        return substance_painter.export.export_project_textures(self.to_json())