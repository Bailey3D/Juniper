import juniper

import juniper.runtime.types.math.vector
import juniper.runtime.widgets


result = juniper.runtime.widgets.query_user(
    "Example",
    "Description",
    ("Yes", "No", "Cancel")
)

print(result)
import juniper.utilities.filemgr
print(juniper.utilities.filemgr.checksum(r"Y:\Juniper3D (Workspace)\Binaries\Juniper\juniper_install.bat"))


'''class Vector3(juniper.runtime.types.math.vector.Vector3):
    #def some_function(self):
    #    return 3333
    #def example_function(self):
    #    print("Heyo2")
    pass


v1 = Vector3(1.0, 2.0, 3.0)
v2 = Vector3(4.0, 5.0, 6.0)
print(v1.x)
print(v1.get_native_object())
#v1.example_function()
#print(juniper.runtime.types.math.vector.Vector2)
#print(v1 + v2)
#print(v1)
#print("-----")
'''