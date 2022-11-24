"""
Shelf based functions
"""
import substance_painter.resource

import juniper.dcc.utilities.shelf


add_shelf = juniper.dcc.utilities.shelf.add_shelf


def find_resource(resource_name, context=None, max_retries=2):
    """
    Find a resource from its name\n
    :param <str:resource_name> The name of the resource to find\n
    :param [<str:context>] The shelf context to search within - if None we will search all shelves\n
    :param [<bool:max_retries>] Maximum amount of retries when no valid resource is found - a Painter bug may cause a resource to not be found on the first try\n
    :return <ResourceID:resource_id> The ResourceID object if found - else None\n
    """
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
