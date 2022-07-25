import os
import inspect
import functools
from qtpy import QtWidgets, uic

import juniper
import juniper_globals


class ToolWidgetBase(QtWidgets.QWidget):
    def __init__(self, parent=None, title=None, horizontal=False, uic=True):
        """
        Base widget class with extra settings for event binding and window properties
        :param [<QWidget:parent>] The parent widget for this tool window
        :param [<str:title>] The title for this tool widget - defaults to None
        :param [<bool:horizontal>] The default direction for the main layout is vertical - this will switch it to Horizontal
        :param [<bool:uic>] When true a .ui file will be searched for from `__class__.__name__ + __file__` of the outermost class
        """
        super(ToolWidgetBase, self).__init__(parent=parent)

        self._parent = parent
        self._title = title
        self.uic = uic

        self.layout_direction = "horizontal" if horizontal else "vertical"

        self.__initialize_ui()

    # ----------------------------------------------------------------------------------

    def set_title(self, title):
        """
        Sets the title for this widget
        :param <str:title> The title of the widget
        """
        self._title = title
        self.setWindowTitle(title or "")

    # ----------------------------------------------------------------------------------

    def addWidget(self, widget):
        """
        Add a widget to the base layout of this Tool Widget
        :param <QWidget:widget> The widget to add
        """
        if(widget):
            self._q_main_layout.addWidget(widget)

    def addLayout(self, layout):
        """
        Add a layout to the base layout of this Tool Widget
        :param <QLayout:layout> The layout to add
        """
        if(layout):
            self._q_main_layout.addLayout(layout)

    def addStretch(self):
        """
        Add stretch to the main layout
        """
        self._q_main_layout.addStretch()

    # ----------------------------------------------------------------------------------

    def initialize_ui(self):
        """
        Override method used for initializing the UI with Tool specific data
        """
        pass

    def refresh_ui(self):
        """
        Override method used to update the whole UI after a major change to the widget
        """
        pass

    def __initialize_ui(self):
        """
        Base private method used to initialize the UI from the target UIC path
        """

        base_layout_class = QtWidgets.QVBoxLayout if self.layout_direction == "vertical" else QtWidgets.QHBoxLayout
        self._q_main_layout = base_layout_class()
        self.setLayout(self._q_main_layout)

        if(self.uic):
            if(os.path.isfile(self.uic_path)):
                self.ui = uic.loadUi(self.uic_path, baseinstance=self)
            else:
                juniper.log.error("UIC file for Tool Widget  was not found: " + self.uic_path, silent=True)

        self.set_title(self._title)

        self.initialize_ui()
        self.refresh_ui()
        self.show()

    # ----------------------------------------------------------------------------------

    @property
    @functools.lru_cache(8)
    def uic_path(self):
        """
        Searches for the target .ui file path for this Tool Widget
        :return <str:path> The path to the .ui file for this tool if found - else ""
        """
        if(self.uic):
            try:
                target_base_class_path = inspect.getfile(self.__class__)
            except Exception:
                # when called through 'juniper.utilities.script_execution.run_tool'
                # the parent class can be incorrectly seen as an in-built class
                target_base_class_path = juniper_globals.get("__juniper_exec_file_path__")
            uic_path = os.path.join(
                os.path.dirname(target_base_class_path),
                self.__class__.__name__ + ".ui"
            )
            if(os.path.isfile(uic_path)):
                return uic_path
        return ""
