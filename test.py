import juniper
import juniper_dcc
import importlib
import juniper.utilities.script_execution
import juniper.types.math.vector

import juniper.types


'''class JuniperType(object):
    def __init__(self):
        print("This is in juniper type")

    @property
    def native_object(self):
        pass

    def serialize(self):
        pass'''


class ExampleFloat2(juniper.types.JuniperType):
    def __init__(self):
        super(ExampleFloat2, self).__init__()


f = ExampleFloat2()


'''def convert(native_object, target_class):
    import juniper.framework.conversion

    # 1) Check for any overrides for the current host context
    if(juniper.program_context != "python"):
        convert_module_override_name = f"juniper_{juniper.program_context}.conversion"
        if(importlib.util.find_spec(convert_module_override_name)):
            convert_module = importlib.import_module(convert_module_override_name)
            importlib.reload(convert_module)

            native_object_type = type(native_object)
            if(hasattr(convert_module, "get_type")):
                native_object_type = convert_module.get_type(native_object)

            target_method_name = f"{native_object_type}_to_{target_class.__name__}".lower()

            if(hasattr(convert_module, target_method_name)):
                return getattr(convert_module, target_method_name)(native_object)

    # 2) 
    #if(hasattr())


a = pymxs.runtime.point3(0,1,222)
b = convert(a, juniper.types.math.vector.Vector3)

c = pymxs.runtime.point2(55, 56)
d = convert(c, juniper.types.math.vector.Vector2)

print(b)
print(d)'''