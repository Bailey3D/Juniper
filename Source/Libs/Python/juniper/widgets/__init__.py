from qtpy import QtWidgets

import juniper.decorators
import juniper.framework.backend.program
import juniper.widgets.q_standalone_app
from juniper.widgets import q_collapsible_widget, q_v_scroll_layout, q_standalone_app


QCollapsibleWidget = q_collapsible_widget.QCollapsibleWidget
QVScrollLayout = q_v_scroll_layout.QVScrollLayout
QStandaloneApp = q_standalone_app.QStandaloneApp


def get_application():
    """Returns the QApplication instance - creates it if it has not been initialized
    :return <QApplication:out> The QApplication instance"""
    output = QtWidgets.QApplication.instance()
    if(not output):
        return juniper.widgets.q_standalone_app.QStandaloneApp()
    return output


# ---------------------------------------------------------------

@juniper.decorators.virtual_method
def initialize_dcc_window_parenting(widget):
    """Used for certain DCC applications where a widget needs to be parented
    to a main window in a specific way
    :param <QWidget:widget> The widget to parent
    """
    pass


@initialize_dcc_window_parenting.override("ue4")
def _initialize_dcc_window_parenting(widget):
    import unreal
    unreal.parent_external_window_to_slate(
        widget.winId(),
        unreal.SlateParentWindowSearchMethod.ACTIVE_WINDOW
    )


# ---------------------------------------------------------------

@juniper.decorators.virtual_method
def get_dcc_main_window():
    """Gets the main QMainWindow object for the current host DCC application
    :return <QMainWindow:main_window> The main window object if found - else None
    """
    get_application()  # by default just ensure the app is created
    return None


@get_dcc_main_window.override("python")
def _get_dcc_main_window():
    app = get_application()
    if(hasattr(app, "main_window")):
        return app.main_window


@get_dcc_main_window.override("max")
def _get_dcc_main_window():
    import qtmax
    return qtmax.GetQMaxMainWindow()


@get_dcc_main_window.override("designer")
def _get_dcc_main_window():
    import juniper.framework.programs.designer.instance
    return juniper.framework.programs.designer.instance.get_main_qt_window()


@get_dcc_main_window.override("houdini")
def _get_dcc_main_window():
    import hou
    return hou.qt.mainWindow()


@get_dcc_main_window.override("painter")
def _get_dcc_main_window():
    import substance_painter.ui
    return substance_painter.ui.get_main_window()


# ---------------------------------------------------------------

def get_dcc_hwnd():
    """Attempts to find the HWND for the current DCC
    :return <int:hwnd> The window handle
    """
    q_main_window = get_dcc_main_window()
    if(not q_main_window):
        import ctypes
        user32 = ctypes.windll.user32
        h_wnd = user32.GetForegroundWindow()
        return h_wnd
    return q_main_window.winId()


def create_dialog(*args, **kwargs):
    """Creates a dialog widget containing instances of all input child widget classes
    :param <[class]:args> Array containing all classes that should be added to the dialog
    :return <QDialog:dialog> The created dialog
    """
    title = kwargs["title"] if "title" in kwargs and kwargs["title"] else "Dialog"
    dialog = QtWidgets.QDialog(parent=get_dcc_main_window())
    dialog.setWindowTitle(title)
    dialog_layout = QtWidgets.QVBoxLayout()
    dialog.setLayout(dialog_layout)
    for i in args:
        i_inst = i()
        dialog_layout.addWidget(i_inst)
    initialize_dcc_window_parenting(dialog)
    dialog.show()
    return dialog
