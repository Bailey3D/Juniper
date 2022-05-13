"""
Singleton based logic
"""


class Singleton(type):
    """
    Base class for a singleton type

    Ie:
    ```
    class ExampleSingleton(metaclass=singleton):
        def __init__(self):
            abc = 123

    print(ExampleSingleton().abc)
    ```
    """
    __instance__ = None

    def __call__(cls, *args, **kwargs):
        if(not cls.__instance__):
            cls.__instance__ = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance__
