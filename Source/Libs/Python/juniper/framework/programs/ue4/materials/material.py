import os
import unreal

import juniper
import juniper.math.vector


def is_material_instance(material):
    """
    Gets whether an input material object is a material instance
    :param <UMaterial:material> The unreal material object to query
    :return <bool:is_material_instance> True if the input is a material instance - else False
    """
    # Do we need to include MaterialInstanceDynamic? Is that ever editable outside of runtime?
    return isinstance(material, unreal.MaterialInstanceConstant)

# --------------------------------------------------------------------


def set_texture_parameter_value(material_instance, parameter_name, texture_path):
    """
    Set a texture path on a material to a texture, relative to unreal
    Note: It doesn't seem like we can set parameters on Materials, only Material Instances..
    :param <MaterialInstance:material_instance> Material instance to alter
    :param <str:parameter_name> The name of the parameter to set
    :param <str:texture_path> Unreal path to the texture to set this parameter to (Ie, "/Game/textures/t_some_tex")
    :return <bool:success> True if the parameter was set - else False
    """
    if(not unreal.EditorAssetLibrary.find_asset_data(texture_path).get_asset()):
        return False
    texture_asset = unreal.EditorAssetLibrary.find_asset_data(texture_path).get_asset()
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_instance, parameter_name, texture_asset)
    return True


def get_texture_parameter_value(material, parameter_name):
    # Should we add a texture wrapper class to make things easier?
    if(is_material_instance(material)):
        material_func = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value
    else:
        material_func = unreal.MaterialEditingLibrary.get_material_default_texture_parameter_value
    return material_func(material, parameter_name)


def get_texture_parameter_names(material):
    """
    :return <[str]:names> The names of all vector parameters on this material
    """
    return unreal.MaterialEditingLibrary.get_texture_parameter_names(material)


def get_texture_parameters(material):
    """
    Gets the values of all texture parameters on a material
    :param <Material:material> The unreal material to process
    :return <{str:str}:parameters> Gets all texture parameter values for the input material
    """
    output = {}
    for i in get_texture_parameter_names:
        output[i] = get_texture_parameter_value(material, i)
    return output

# --------------------------------------------------------------------


def set_bool_parameter_value(material, parameter_name, parameter_value):
    juniper.log.error("Cannot set Bool parameter on unreal materials..")
    return False


def get_bool_parameter_value(material, parameter_name):
    if(is_material_instance(material)):
        material_func = unreal.MaterialEditingLibrary.get_material_instance_static_switch_parameter_value
    else:
        material_func = unreal.MaterialEditingLibrary.get_material_default_static_switch_parameter_value
    return material_func(material, parameter_name)


def get_bool_parameter_names(material):
    """
    :return <[str]:names> The names of all bool parameters on this material
    """
    return unreal.MaterialEditingLibrary.get_static_switch_parameter_names(material)


def get_bool_parameters(material):
    """
    Gets the values of all vector parameters on a material
    :param <Material:material> The unreal material to process
    :return <[str:Vector4]:parameters> Gets all vector parameter values for the input material
    """
    output = {}
    for i in get_bool_parameter_names:
        output[i] = get_bool_parameter_value(material)
    return output

# --------------------------------------------------------------------


def set_vector_parameter_value(material, parameter_name, parameter_value):
    """
    Set a vector parameter value on a material
    :param <Material:material> The material to alter - Note: unreal doesn't support setting values on Materials, only Instances
    :param <str:parameter_name> The name of the parameter to set
    :param <VectorType:parameter_value> The value to set to, any type with an "as_linear_color" property is supported
    :return <bool:success> True if set - else False
    """
    if(is_material_instance(material)):
        material_func = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value
        material_func(material, parameter_name, parameter_value.as_linear_color())
        return True
    juniper.log.error("Cannot set parameters on Material type - only Material Instance!")
    return False


def get_vector_parameter(material, parameter_name):
    if(is_material_instance(material)):
        material_func = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value
    else:
        material_func = unreal.MaterialEditingLibrary.get_material_default_vector_parameter_value
    output = material_func(material, parameter_name)
    return juniper.math.vector.Vector4(output.x, output.y, output.z, output.w)


def get_vector_parameter_names(material):
    """
    :return <[str]:names> The names of all vector parameters on this material
    """
    return unreal.MaterialEditingLibrary.get_vector_parameter_names(material)


def get_vector_parameters(material):
    """
    Gets the values of all vector parameters on a material
    :param <Material:material> The unreal material to process
    :return <[str:Vector4]:parameters> Gets all vector parameter values for the input material
    """
    output = {}
    for i in get_vector_parameter_names:
        unreal_value = get_vector_parameter(material)
        output[i] = juniper.math.vector.Vector4(unreal_value.r, unreal_value.g, unreal_value.b, unreal_value.a)
    return output

# --------------------------------------------------------------------


def set_float_parameter_value(material, parameter_name, parameter_value):
    """
    Set a float parameter value on a material
    :param <Material:material> The material to alter - Note: unreal doesn't support setting values on Materials, only Instances
    :param <str:parameter_name> The name of the parameter to set
    :param <float:parameter_value> The value to set to
    :return <bool:success> True if set - else False
    """
    if(is_material_instance(material)):
        material_func = unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value
        material_func(material, parameter_name, parameter_value)
        return True
    juniper.log.error("Cannot set parameters on Material type - only Material Instance!")
    return False


def get_float_parameter_value(material, parameter_name):
    if(is_material_instance(material)):
        material_func = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value
    else:
        material_func = unreal.MaterialEditingLibrary.get_material_default_scalar_parameter_value
    return material_func(material, parameter_name)


def get_float_parameter_names(material):
    """
    :return <[str]:names> The names of all float parameters on this material
    """
    return unreal.MaterialEditingLibrary.get_scalar_parameter_names(material)


def get_float_parameters(material):
    """
    Gets the values of all float parameters on a material
    :param <Material:material> The unreal material to process
    :return <[str:float]:parameters> Gets all float parameter values for the input material
    """
    output = {}
    for i in get_float_parameter_names:
        output[i] = get_float_parameter_value(material)
    return output

# --------------------------------------------------------------------


def set_two_sided(material, state, save=False):
    """
    Sets whether this unreal material is two sided
    Note: Only material instances are currently supported
    :param <UMaterial:material> The material to set
    :param <bool:state> Whether this is two sided or not
    """
    if(not is_material_instance(material)):
        return False

    base_property_overrides = material.get_editor_property("base_property_overrides")
    # remember to set properties to be overriden before setting the property
    # if not then the property will not be altered!
    base_property_overrides.set_editor_property("override_two_sided", True)
    base_property_overrides.set_editor_property("two_sided", True)
    material.set_editor_property("base_property_overrides", base_property_overrides)

    if(save):
        save_material(material)

    return True

# --------------------------------------------------------------------


def set_parameter(material, parameter_name, parameter_value):
    """
    Sets a parameter on a material, automatically determines type
    :param <UMaterial:material> The material to set the parameter on
    :param <str:parameter_name> The name of the parameter to set
    :param <type:parameter_value> The value to set the parameter to
    :return <bool:success> True if set - else False
    """
    if(not is_material_instance(material)):
        return False

    if(type(parameter_value) in (float, int)):
        return set_float_parameter_value(material, parameter_name, parameter_value)
    elif(isinstance(parameter_value, juniper.math.vector._VectorType)):
        return set_vector_parameter_value(material, parameter_name, parameter_value)
    elif(type(parameter_value) == bool):
        return set_bool_parameter_value(material, parameter_name, parameter_value)

    return False

# --------------------------------------------------------------------


def save_material(material_asset, force=False):
    """
    Save a material UAsset
    :param <UMaterial:material> The material to save
    :param [<bool:force>] Should this be saved even if not updated?
    """
    unreal.EditorAssetLibrary.save_loaded_asset(material_asset, only_if_is_dirty=force)


def create_material_instance(new_upath, parent_upath, save=False):
    """
    Creates a new material instance
    :param <str:new_upath> Unreal path for this material
    :param <str:parent_upath> Unreal path to the parent material
    :param [<bool:save>] Should this asset be saved?
    :return <UMaterial:material> The generated or found material asset
    """
    asset_name = os.path.basename(new_upath)
    asset_dir = os.path.dirname(new_upath)
    child_exists = unreal.EditorAssetLibrary.does_asset_exist(new_upath)
    parent_exists = unreal.EditorAssetLibrary.does_asset_exist(parent_upath)

    parent = None
    output = None

    if(child_exists):
        output = unreal.EditorAssetLibrary.find_asset_data(new_upath).get_asset()
    else:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        output = asset_tools.create_asset(
            asset_name,
            asset_dir,
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew()
        )
        child_exists = True

    if(parent_exists):
        parent = unreal.EditorAssetLibrary.find_asset_data(parent_upath).get_asset()
        unreal.MaterialEditingLibrary.set_material_instance_parent(output, parent)

    if(child_exists and save):
        try:
            save_material(output, force=True)
        except Exception:
            pass

    return output
