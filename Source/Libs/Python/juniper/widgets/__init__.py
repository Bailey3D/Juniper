from qtpy import QtWidgets

import juniper.engine
import juniper.decorators
import juniper.widgets.q_standalone_app
from juniper.widgets import q_collapsible_widget, q_v_scroll_layout, q_standalone_app


QCollapsibleWidget = q_collapsible_widget.QCollapsibleWidget
QVScrollLayout = q_v_scroll_layout.QVScrollLayout
QStandaloneApp = q_standalone_app.QStandaloneApp

get_application = juniper.engine.JuniperEngine().get_qt_application
initialize_host_window_parenting = juniper.engine.JuniperEngine().register_qt_widget
get_main_window = juniper.engine.JuniperEngine().get_main_window


# ---------------------------------------------------------------

def get_host_hwnd():
    """
    Attempts to find the HWND for the current host application
    :return <int:hwnd> The window handle
    """
    q_main_window = get_main_window()
    if(not q_main_window):
        import ctypes
        user32 = ctypes.windll.user32
        h_wnd = user32.GetForegroundWindow()
        return h_wnd
    return q_main_window.winId()


def create_dialog(*args, **kwargs):
    """
    Creates a dialog widget containing instances of all input child widget classes
    :param <[class]:args> Array containing all classes that should be added to the dialog
    :return <QDialog:dialog> The created dialog
    """
    title = kwargs["title"] if "title" in kwargs and kwargs["title"] else "Dialog"
    dialog = QtWidgets.QDialog(parent=get_main_window())
    dialog.setWindowTitle(title)
    dialog_layout = QtWidgets.QVBoxLayout()
    dialog.setLayout(dialog_layout)
    for i in args:
        i_inst = i()
        dialog_layout.addWidget(i_inst)
    initialize_host_window_parenting(dialog)
    dialog.show()
    return dialog
