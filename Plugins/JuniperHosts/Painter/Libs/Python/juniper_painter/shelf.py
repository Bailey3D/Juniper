"""
Shelf based functions
"""
import winreg


def add_shelf(shelf_name, shelf_path, shelf_status):
    """
    Adds a new shelf to the painter registry
    :param <str:shelf_name> Name of the shelf to add, must be lower case
    :param <str:shelf_path> Absolute path to the shelf
    :param <bool:shelf_status> False = enabled, True = disabled
    """
    painter_reg_name = "Software\\Allegorithmic\\Substance Painter\\Shelf\\pathInfos"

    shelf_name = shelf_name.lower()
    shelf_path = shelf_path.replace("\\", "/")
    shelf_path = shelf_path if (shelf_path[-1] != "/") else shelf_path[0:-1]
    shelf_status = "false" if shelf_status else "true"

    # load the key "reg_name" and build the shelf registry path
    # Note: Is this still under the same key since the switch to Adobe accounts?
    painter_reg_name = "Software\\Allegorithmic\\Substance Painter\\Shelf\\pathInfos"

    #
    reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)

    key = winreg.OpenKey(reg_connection, painter_reg_name, winreg.KEY_READ)
    subkey_count = winreg.QueryInfoKey(key)[0]

    shelf_number = 0
    already_exists = False

    for x in range(subkey_count):
        subkey_name = winreg.EnumKey(key, x)

        target_key = winreg.OpenKey(key, subkey_name, 0, winreg.KEY_ALL_ACCESS)
        target_key_name = winreg.QueryValueEx(target_key, "name")[0]

        # if we find a key with the target name - update the path
        if(target_key_name == shelf_name):
            already_exists = True
            winreg.SetValueEx(target_key, "disabled", 0, winreg.REG_SZ, shelf_status)
            winreg.SetValueEx(target_key, "name", 0, winreg.REG_SZ, shelf_name)
            winreg.SetValueEx(target_key, "path", 0, winreg.REG_SZ, shelf_path)

        target_key.Close()

        if(int(subkey_name) > shelf_number):
            shelf_number = int(subkey_name)

    shelf_number += 1

    if(not already_exists):
        new_key = winreg.CreateKey(key, str(shelf_number))
        winreg.SetValueEx(new_key, "disabled", 0, winreg.REG_SZ, shelf_status)
        winreg.SetValueEx(new_key, "name", 0, winreg.REG_SZ, shelf_name)
        winreg.SetValueEx(new_key, "path", 0, winreg.REG_SZ, shelf_path)

        new_key.Close()
        key.Close()

    # increase shelf count if needed
    key = winreg.OpenKey(reg_connection, painter_reg_name, 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, "size", 0, winreg.REG_DWORD, winreg.QueryInfoKey(key)[0])
    key.Close()


def find_resource(resource_name, context=None, max_retries=2):
    """
    Find a resource from its name
    :param <str:resource_name> The name of the resource to find
    :param [<str:context>] The shelf context to search within - if None we will search all shelves
    :param [<bool:max_retries>] Maximum amount of retries when no valid resource is found - a Painter bug may cause a resource to not be found on the first try
    :return <ResourceID:resource_id> The ResourceID object if found - else None
    """
    import substance_painter.resource
    if(not context):
        for i in substance_painter.resource.Shelves.all():
            possible_resource = substance_painter.resource.ResourceID(context=i.name(), name=resource_name)
            resource_handle = substance_painter.resource.Resource.retrieve(possible_resource)
            if(resource_handle != []):
                return possible_resource
    else:
        possible_resource = substance_painter.resource.ResourceID(context=context, name=resource_name)
        resource_handle = substance_painter.resource.Resource.retrieve(possible_resource)
        if(possible_resource != []):
            return possible_resource

    if(max_retries > 0):
        # for some reason a resource may return None the first time it is loaded in Painter
        # run N times if this is the case to see if we can bypass this bug
        return find_resource(resource_name, context=context, max_retries=(max_retries - 1))

    return None