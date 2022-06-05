"""
Python library for this plugin
"""
#  Each plugin automatically gets its `Source\\Libs\\Python\\..` folder added to sys.path on Juniper startup
#  this enables the use of custom Python packages
#
#  Example usage:
#
#  ```
#  import juniper_plugin_template
#  juniper_plugin_template.example_function()
#  ```


def example_function(param_1, param_2=None):
    """
    This is an example function - with example docstrings.\n
    :param <int:param_1> This defines an arg param - type is defined as int\n
    :param [<str:param_2>] This defines an optional param - type is defined as str. The "[" "]" denote it is optional.\n
    :return <bool:output> This defines a return type - in this case a bool.\n
    """
    print(param_1)
    print(param_2)
    return True
