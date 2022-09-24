# TODO~: Implementation
# compression_method
# hash(hash_size)
# texture_type
# uses_srgb
# parameter_name
# import_asset
import juniper.types.wrappers.type_wrapper


class TextureWrapperManager(juniper.types.wrappers.type_wrapper.TypeWrapperManager):
    pass


class TextureWrapper(juniper.types.wrappers.type_wrapper.TypeWrapper):
    __manager__ = TextureWrapperManager

    def __init__(self, native_object, asset_path=None):
        """
        Wrapper class for a Texture type object
        :wraps <unreal:UTexture>
        :param <NativeType:native_object> The native object to wrap
        :param [<str:asset_path>] Path to a real texture (Ie, .tga, .png) - if we're wrapping this then native_object should be left blank
        """
        super().__init__(native_object)
