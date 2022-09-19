"""
Contains base class implementations for Type Wrappers

Type wrappers are used to wrap native object types from various host applications into a common Juniper type.
Each wrapper includes a base class for functionality, and a manager class for caching and retrieving initialized wrapper objects.
"""
import juniper
import juniper.types
import juniper.decorators
from juniper.types.framework.singleton import Singleton


class TypeWrapperManager(juniper.types.Manager, metaclass=Singleton):
    __instance__ = None

    def __init__(self):
        """
        Manager class used for caching / registering wrapper objects
        """
        self.__stored_objects = []
        self.__stored_objects_native_objects_cache = []

    def register(self, object_wrapper):
        """
        Registers an TypeWrapper
        :param <TypeWrapper:object_wrapper> The TypeWrapper to register
        :return <TypeWrapper:registered_wrapper> The newly registered wrapper if it did not already exist - else the cached TypeWrapper
        """
        possible_index = self.index(object_wrapper)
        if(possible_index is not None):
            return self.__stored_objects[possible_index]
        else:
            self.__stored_objects.append(object_wrapper)
            self.__stored_objects_native_objects_cache.append(object_wrapper.native_object)
            return object_wrapper

    def index(self, target):
        """
        Finds the index of an TypeWrapper from either an input TypeWrapper object or a native object
        :param <object:target> The target to find the index of - this can be an initialized TypeWrapper reference or a native object to search for
        :return <int:index> The index of the target
        """
        if(isinstance(target, TypeWrapper)):
            if(target in self.__stored_objects):
                # for raw TypeWrapper references look for it directly in the base cache
                return self.__stored_objects.index(target)
        elif(target in self.__stored_objects_native_objects_cache):
            # else for a possible native_object input search for it in the
            # native objects cache and return the real TypeWrapper
            return self.__stored_objects_native_objects_cache.index(target)
        '''else:
            # if all else fails the wrapped object may be reinitializing each gather in the host application
            # resulting in objects that are referencing the same node but have different python memory addresses
            # brute force an equality comparison to see if we can find a match
            for i in range(len(self.__stored_objects_native_objects_cache)):
                print(target)
                print(self.__stored_objects_native_objects_cache[i])
                if(self.__stored_objects_native_objects_cache[i] == target):
                    return self.__stored_objects[i]'''
        return None

    def find(self, target):
        """
        Finds a cached TypeWrapper from either an input TypeWrapper object or a native object
        :param <object:target> The target to find the index of - this can be an initialized TypeWrapper reference or a native object to search for
        :return <TypeWrapper:index> The cached TypeWrapper - or None if it doesn't exist
        """
        possible_index = self.index(target)
        if(possible_index is not None):
            return self.__stored_objects[possible_index]
        return None

    def unregister(self, object_wrapper):
        """
        Unregisters a TypeWrapper if it has been registered - freeing the stored native_object from memory
        :param <TypeWrapper:object_wrapper> The object wrapper to unregister
        """
        possible_index = self.index(object_wrapper)
        if(possible_index is not None):
            self.__stored_objects[possible_index].invaildate()
            self.__stored_objects.pop(possible_index)
            self.__stored_objects_native_objects_cache.pop(possible_index)


class TypeWrapper(juniper.types.Object):
    __manager__ = TypeWrapperManager

    def __init__(self, native_object):
        """
        Wrapper class for a type from the current host application (Ie, Node in 3DS Max, Actor in Unreal)

        An explicit manager class can be used for caching by setting the `__manager__` property to the class
        in the main class body
        """
        self.native_object = native_object

    def __new__(cls, native_object):
        """
        Override for __new__ to add support for TypeWrapperManager caching to avoid construction each gather
        """
        possible_index = cls.__manager__().index(native_object)
        if(possible_index is not None):
            output = cls.__manager__().find(native_object)
        else:
            output = super().__new__(cls)
            output.__init__(native_object)
            cls.__manager__().register(output)
        return output

    # -------------------------------------------------------

    @property
    def valid(self):
        """
        Gets the validity of this node / wrapper
        :return <bool:validity> True if the node is valid - else False
        """
        return self.get_validity()

    @juniper.decorators.virtual_method
    def get_validity(self):
        if(self.native_object):
            return True
        return False

    def invalidate(self):
        """
        Invalidates this wrapper object
        """
        self.native_object = None
