import os
import sys
from qtpy import QtWidgets, QtGui
from scss import Scss

import juniper.paths


class QStandaloneApp(QtWidgets.QApplication):
    """A Juniper base QApplication with custom styling"""
    def __init__(self):
        super(QStandaloneApp, self).__init__(sys.argv)

        self.set_icon(os.path.join(juniper.paths.root(), "Resources\\Icons\\Standard\\app_default.png"))
        self.apply_stylesheet()

    def set_icon(self, icon_path):
        """Set the application icon"""
        self.icon = QtGui.QIcon()
        self.icon.addFile(icon_path)
        self.setWindowIcon(self.icon)

    def apply_stylesheet(self, stylesheet_path=None):
        """Initialize the styling for the application
        :param [<str:stylesheet_path>] Absolute path to the stylesheet to apply
        """
        if(not stylesheet_path):
            stylesheet_path = os.path.join(juniper.paths.root(), "Config\\Styles\\standalone.scss")

        self.setStyle(QtWidgets.QStyleFactory.create("fusion"))
        with open(stylesheet_path, "r") as f:
            self.setStyleSheet(Scss().compile(f.read()))

    @property
    def main_window(self):
        """Searches / returns the first QMainWindow for the application
        :return <QMainWindow:main_window> The main window if found - else None
        """
        for i in self.topLevelWidgets():
            if(isinstance(i, QtWidgets.QMainWindow)):
                return i
        return None
