import juniper


def program_context(context):
    """
    Decorator used to ensure a function is not called outside of a certain program context

    Example Usage
    ```
    @juniper.decorators.program_context("ue4")
    def example_function():
        pass
    ```
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if(juniper.program_context == context):
                return func(*args, **kwargs)
            else:
                assert False, (f"{__file__}: The method \"{func.__name__}\" cannot be called outside of {context}")
        return wrapper
    return decorator


def virtual_method(func):
    """
    Decorator for a Juniper method which supports overrides for the different
    program contexts (Ie, ue4, max, python)

    Example Usage
    ```
    @juniper.decorators.virtual_method
    def some_method():
        print("Base implementation of this method - ran when there is no override")

    @some_method.override("ue4"):
    def __some_method():
        print("This will be overriden when ran from Unreal!")
    ```

    Note: The "__" prefix on overriden functions is not required - but should be done where possible as
    it ensures the base implementation's docstring is shown (as opposed to the last implemented override)
    """
    def wrapper(*args, **kwargs):
        if(func.__juniper_override__):
            return func.__juniper_override__(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    def __override(target_program_context):
        def __override_decorator(override_func):
            if(target_program_context == juniper.program_context):
                def __override_wrapper(*args, **kwargs):
                    return override_func(*args, **kwargs)
                setattr(func, "__juniper_override__", override_func)
                setattr(__override_wrapper, "override", __override)
                return __override_wrapper
            else:
                return wrapper
        return __override_decorator

    setattr(wrapper, "override", __override)
    setattr(func, "__juniper_override__", None)
    return wrapper


class classproperty(property):
    """
    Decorator used for combining @staticmethod and @property
    """
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
