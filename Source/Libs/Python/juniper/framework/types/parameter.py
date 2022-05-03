import functools
from enum import Enum


class ParameterTypes(Enum):
    """Enum containing the names of all valid parameter types"""
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


class __ParameterManager(object):
    """Singleton manager class for parameters"""
    __instance__ = None


    def get_parameter_type(self, value):
        """Takes an input parameter of X type and finds the type"""
        if(type(value) in [list, tuple]):
            if(all(isinstance(x, int) for x in value)):
                t = "int"
            else:
                t = "float"
            l = "" if len(value) == 1 else str(len(value))
            return ParameterTypes[t + l]

        elif(value in [True, False, "true", "false", "True", "False"]):
            return ParameterTypes["bool"]

        elif(type(value) == float):
            return ParameterTypes["float"]

        elif(type(value) == int):
            return ParameterTypes["int"]
        return ParameterTypes["unknown"]


if(__ParameterManager.__instance__ is None):
    __ParameterManager.__instance__ = __ParameterManager()
ParameterManager = __ParameterManager.__instance__


class Parameter(object):
    """Class for a generic parameter type"""
    def __init__(self, name="", description="", value="", default="", min="", max="", group=""):
        self.name = name
        self.value = value
        self.description = description
        self.default = default
        self.min = min
        self.max = max

    @property
    @functools.lru_cache()
    def type(self):
        """get the type for this parameter fro the rest of its stored data"""
        return ParameterManager.get_parameter_type(self.value)

    @staticmethod
    def from_dict(data):
        """generate a parameter from an input data dict"""
        return Parameter(
            name = data["name"] if "name" in data else "",
            description = data["description"] if "description" in data else "",
            default = data["default"] if "default" in data else "",
            group = data["group"] if "group" in data else "",
            min = data["min"] if "min" in data else "",
            max = data["max"] if "max" in data else ""
        )
