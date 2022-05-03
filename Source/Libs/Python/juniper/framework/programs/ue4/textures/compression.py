import unreal


def get_unreal_compression_method(method_string):
    """
    Takes an Unreal Compression method string and returns the matchingunreal object
    :param <str:method_string> The compression method (Ie, "TC_NORMALMAP")
    :return <unreal.TextureCompressionSetting:output> The compression setting type
    """
    return eval("unreal.TextureCompressionSettings." + method_string)
