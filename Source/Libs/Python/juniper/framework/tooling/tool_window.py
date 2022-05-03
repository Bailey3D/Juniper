import juniper
import juniper.widgets

from . import tool_widget_base


class ToolWindow(tool_widget_base.ToolWidgetBase):
    def __init__(self, parent=None, title="ToolWindow", horizontal=False, uic=True):
        """
        Instance of ToolWidgetBase used for tools which should be displayed as a standalone window
        :param [<QWidget:parent>] The parent widget for this tool window
        :param [<str:title>] The title for this tool widget - defaults to None
        :param [<bool:horizontal>] The default direction for the main layout is vertical - this will switch it to Horizontal
        :param [<bool:uic>] When true a .ui file will be searched for from `__class__.__name__ + __file__` of the outermost class
        """
        super(ToolWindow, self).__init__(parent=parent, title=title, horizontal=horizontal, uic=uic)
        juniper.widgets.initialize_dcc_window_parenting(self)
