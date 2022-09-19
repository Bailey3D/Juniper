import functools
from enum import Enum

import juniper
import juniper.types
import juniper.types.framework.singleton


class ParameterTypes(Enum):
    """
    Enum containing the names of all valid parameter types
    """
    unknown = 0
    float = 1
    float2 = 2
    float3 = 3
    float4 = 4
    int = 5
    int2 = 6
    int3 = 7
    int4 = 8
    bool = 9
    texture = 10


class ParameterManager(juniper.types.Manager, metaclass=juniper.types.framework.singleton.Singleton):
    """
    Singleton manager class for parameters
    """

    def get_parameter_type(self, value):
        """
        Takes an input parameter of X type and finds the type
        :param <object:value> The value to get the type for
        """
        if(type(value) in [list, tuple]):
            if(all(isinstance(x, int) for x in value)):
                type_ = "int"
            else:
                type_ = "float"
            length = "" if len(value) == 1 else str(len(value))
            return ParameterTypes[type_ + length]

        elif(value in [True, False, "true", "false", "True", "False"]):
            return ParameterTypes["bool"]

        elif(type(value) == float):
            return ParameterTypes["float"]

        elif(type(value) == int):
            return ParameterTypes["int"]
        return ParameterTypes["unknown"]


class Parameter(juniper.types.Object):
    def __init__(self, name="", description="", value="", default="", min="", max="", group=""):
        """
        Class for a generic parameter type
        :param [<str:name>] The name of the parameter
        :param [<str:description>] Description of the parameter
        :param [<object:value>] The value to set (must be JSON serializeable)
        :param [<object:default>] The default value (must be JSON serializeable)
        :param [<object:min>] The minimum value (where applicable - Ie, floats)
        :param [<object:max>] The maximum value (where applicable - Ie, floats)
        :param [<str:group>] The name of the group for this parameter (Ie, for parameter editors)
        """
        self.name = name
        self.value = value
        self.description = description
        self.default = default
        self.min = min
        self.max = max

    @property
    @functools.lru_cache()
    def type(self):
        """
        get the type for this parameter fro the rest of its stored data
        """
        return ParameterManager().get_parameter_type(self.value)

    @staticmethod
    def from_dict(data):
        """
        generate a parameter from an input data dict
        :param <dict:data> The dict to convert
        :return <Parameter:param> The dict as a parameter
        """
        return Parameter(
            name=data["name"] if "name" in data else "",
            description=data["description"] if "description" in data else "",
            default=data["default"] if "default" in data else "",
            group=data["group"] if "group" in data else "",
            min=data["min"] if "min" in data else "",
            max=data["max"] if "max" in data else ""
        )
