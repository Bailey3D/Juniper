from . import tool_widget_base


class ToolPanel(tool_widget_base.ToolWidgetBase):
    def __init__(self, parent=None, title="ToolPanel", horizontal=False, uic=True):
        """
        Instance of ToolWidgetBase used for planel type tools (widgets which can be added as children - no standalone window)
        :param [<QWidget:parent>] The parent widget for this tool window
        :param [<str:title>] The title for this tool widget - defaults to None
        :param [<bool:horizontal>] The default direction for the main layout is vertical - this will switch it to Horizontal
        :param [<bool:uic>] When true a .ui file will be searched for from `__class__.__name__ + __file__` of the outermost class
        """
        super(ToolPanel, self).__init__(parent=parent, title=title, horizontal=horizontal, uic=uic)
