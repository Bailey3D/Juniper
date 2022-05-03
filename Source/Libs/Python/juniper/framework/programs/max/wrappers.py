import pymxs


class CoordSys(object):
    def __init__(self, target_coordsys):
        """
        Class used inside a `with` statement to temporarily change coordinate systems
        The same as `in coordsys target` from Maxscript

        Valid coordinate systems include:
        - local
        - world
        - parent
        - grid
        - screen

        :param <str:target_coordsys> The target coordsyst

        ```
        with CoordSys("local") as cs:
            pass
        ```
        """
        self.__target_coordsys = pymxs.runtime.name(target_coordsys)
        self.__coordsys = getattr(pymxs.runtime, "%coordsys_context")
        self.__previous_coordsys = None

    def __enter__(self):
        self.__previous_coordsys = self.__coordsys(self.__target_coordsys, None)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__coordsys(self.__previous_coordsys, None)
