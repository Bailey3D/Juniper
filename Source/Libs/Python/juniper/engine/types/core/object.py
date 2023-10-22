# TODO~ Juniper Engine: Implementation
"""
"""
import os
import juniper
import juniper.engine.paths
import juniper.engine.override

juniper_root = juniper.engine.paths.root()
juniper_host = juniper.program_context
juniper_host_root = os.path.join(juniper_root, "Source\\Hosts", juniper_host) if juniper_host else None


class Example():
    pass


class _ObjectMeta(type):
    pass


class Object(object, metaclass=_ObjectMeta):

    def __cast__(self):
        pass

    def __serialize__(self):
        pass

    def __deserialize__(self):
        pass

    # ----------------------------------------------------------

    def __getattribute__(self, __name):
        return super(Object, self).__getattribute__(__name)

    #def __getattr__(self, name):
    #    print("geting!")
    #    return super.__getattribute__(self, name)
