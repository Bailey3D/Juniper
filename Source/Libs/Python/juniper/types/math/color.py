"""
Wrapper for a simple colour type
"""
import juniper.decorators
import juniper.math


class Color(object):
    def __init__(self, *args):
        """
        Base class for a colour type
        In [0..1] range
        """
        if(len(args) == 1):
            if(isinstance(args[0], str)):
                self._data = self._from_hex_value(args[0])
            else:
                self._data = self._from_native_object(args[0])
        elif(len(args) == 3):
            self._data = (args[0], args[1], args[2], 1.0)
        elif(len(args) == 4):
            self._data = (args[0], args[1], args[2], args[3])
        else:
            raise AttributeError
        self._data = [juniper.math.saturate(x) for x in self._data]

    def _from_hex_value(self, hex_value):
        """
        Creates a colour from a hex value
        :param <str:hex_value> The hex value to convert
        :return <Color:color> The colour object
        """
        hex_value = hex_value.lstrip('#')
        lv = len(hex_value)
        output = list(int(hex_value[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))
        if(len(output) < 4):
            output.append(1.0)
        return output

    # ------------------------------------------------------------

    @property
    def native_object(self):
        """
        Gets a version of this as the native type for the current DCC
        :return <value:native_type> The native type where possible - else None
        """
        return self.get_native_object()

    @juniper.decorators.virtual_method
    def get_native_object(self):
        raise NotImplementedError

    @juniper.decorators.virtual_method
    def _from_native_object(self, native_object):
        """
        Creates a new instance of this type from the input type
        """
        raise NotImplementedError

    # ------------------------------------------------------------

    def __repr__(self):
        return f"{type(self).__name__}{tuple(self._data)}"

    # ------------------------------------------------------------

    @property
    def r(self):
        return self._data[0]

    @r.setter
    def r(self, value):
        self._data[0] = juniper.math.saturate(value)

    @property
    def g(self):
        return self._data[1]

    @g.setter
    def g(self, value):
        self._data[1] = juniper.math.saturate(value)

    @property
    def b(self):
        return self._data[2]

    @b.setter
    def b(self, value):
        self._data[2] = juniper.math.saturate(value)

    @property
    def a(self):
        return self._data[3]

    @a.setter
    def a(self, value):
        self._data[3] = juniper.math.saturate(value)

    # ------------------------------------------------------------

    @property
    def css(self):
        """
        Gets a CSS formatted string of this colour
        :return <str:output> The colour formatted for CSS (Ie, "rgba(1.0, 0.0, 0.0, 1.0")
        """
        return f"rgba({int(self.r * 255)}, {int(self.g * 255)}, {int(self.b * 255)}, {int(self.a * 255)})"

    @property
    def qcolor(self):
        """
        Gets this Color object as a Qt based QColor object
        :return <QColor:output> The colour converted to a QColor
        """
        from qtpy import QtGui
        return QtGui.QColor(self.r * 255, self.g * 255, self.b * 255, self.a * 255)
