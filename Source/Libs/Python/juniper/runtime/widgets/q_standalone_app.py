import os
import sys
from qtpy import QtWidgets, QtGui
import sass

import juniper.engine.paths
import juniper.engine.resources


class QStandaloneApp(QtWidgets.QApplication):
    def __init__(self):
        """
        A Juniper base QApplication with custom styling
        """
        super(QStandaloneApp, self).__init__(sys.argv)

        self.set_icon(juniper.engine.resources.default_icon_path())
        self.apply_stylesheet()

    def set_icon(self, icon_path):
        """
        Set the application icon
        :param <str:icon_path> Absolute path to the icon
        """
        self.icon = QtGui.QIcon()
        self.icon.addFile(icon_path)
        self.setWindowIcon(self.icon)

    def apply_stylesheet(self, stylesheet_path=None):
        """
        Initialize the styling for the application
        :param [<str:stylesheet_path>] Absolute path to the stylesheet to apply
        """
        if(not stylesheet_path):
            stylesheet_path = os.path.join(juniper.engine.paths.root(), "Config\\Styles\\standalone.scss")

        self.setStyle(QtWidgets.QStyleFactory.create("fusion"))
        with open(stylesheet_path, "r") as f:
            scss_compiled = sass.compile(string=f.read())
            self.setStyleSheet(scss_compiled)

    @property
    def main_window(self):
        """
        Searches / returns the first QMainWindow for the application
        :return <QMainWindow:main_window> The main window if found - else None
        """
        for i in self.topLevelWidgets():
            if(isinstance(i, QtWidgets.QMainWindow)):
                return i
        return None
