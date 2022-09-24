'''import sys
import juniper
import juniper.engine.types.core.function as f


class B(object):
    def __init__(self) -> None:
        super().__init__()

    @f.function()
    def some_function(self):
        print(self)
        print("This is in A")

    @some_function.override(host="python")
    def some_function(self):
        print("This is in B")

    #@some_function.override(host="peython")
    #def some_function(self):
    #    print("This is in C")

    def something(self):
        pass


b = B()
b.some_function()
print(b.some_function)


#juniper.cast()'''


'''import juniper.types.math.vector as v

a = v.Vector3(0, 1, 2)
print(a)'''

import juniper
print("ok")