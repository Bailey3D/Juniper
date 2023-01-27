# TODO~ Juniper Engine: Complete implementation. Fix the `self` issue
import functools
import inspect
import weakref

import juniper


class Function(object):
    def __init__(self, wraps, **kwargs):
        #self.wraps = wraps
        self.__override = None
        self.__delegates = set()

        self.__deprecated = "deprecated" in kwargs and kwargs["deprecated"] is True
        self.__developer = "developer" in kwargs and kwargs["developer"] is True
        self.__overriding = kwargs["overriding"] if "overriding" in kwargs else None

        @functools.wraps(wraps)
        def __wraps__(*wrapped_args, **wrapped_kwargs):
            return wraps(*wrapped_args, **wrapped_kwargs)
        self.wraps = __wraps__

    def bind(self):
        """
        Binds a function to this function
        :param <func:child> The child function to bind
        """
        raise NotImplementedError

    def override(self, host=None):
        """
        Adds an override for this function - called in place of the base implementation
        Note: A function can have multiple overrides - all of which will be called in place of the parent
        :param <func:base> The base function to override
        """
        def decorator(func):
            if(host in (None, juniper.program_context)):
                func_override = Function(func, overriding=self)
                self.__override = func_override
                return func_override
                #return func_override.wraps
            else:
                #wrapping = self.wraps
                return self
        return decorator

    @staticmethod
    def function_decorator(**kwargs):
        def decorator(func):
            func_override = Function(func, **kwargs)
            return func_override
        return decorator

    @property
    def developer(self):
        """
        Gets whether this function is a developer only function
        :return <bool:state> True if this is developer only - else False
        """
        return self.__developer

    @property
    def deprecated(self):
        """
        Gets whether this function is flagged as deprecated
        :return <bool:state> True if this is a deprecated function - else False
        """
        return self.__deprecated

    @property
    def overriding(self):
        """
        :return <Function:overriding> The function that this function is overriding
        """
        return self.__overriding

    def __call__(self, *args, **kwargs):
        # TODO~ Juniper Engine: Add support to bind delegates to Juniper functions
        # TODO~ Juniper Engine: Validity checks
        # overrides
        if(self.__override):
            self.__override(*args, **kwargs)
        else:
            self.wraps(*args, **kwargs)

    def __str__(self):
        base_str = str(self.wraps).lstrip("<")
        class_str = super().__str__().rstrip(">")
        return f"{class_str} wrapping {base_str}"

    @property
    def outer(self):
        """
        :return <function:outer> The outermost function for this wrapper
        """
        if(not self.overriding):
            return self.wraps
        elif(not isinstance(self.overriding, Function)):
            return self.overriding
        return self.overriding.outer


function = Function.function_decorator
