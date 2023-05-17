from qtpy import QtWidgets, QtGui

import juniper.engine
import juniper.engine.resources
import juniper.engine.decorators
import juniper.runtime.widgets.q_standalone_app
from juniper.runtime.widgets import q_collapsible_widget, q_v_scroll_layout, q_standalone_app


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


# ---------------------------------------------------------------


def query_user(title, description, options, type_=QtWidgets.QMessageBox.Information):
    """
    Queries the user with a simple popup - this uses a dirty way of adding named buttons
    without the need for subclassing
    Note: Only 4 options can be presented currently
    :param <str:title> The title displayed in the titlebar
    :param <str:description> The text to query the user with
    :param <[str]:options> The options to present - the chosen option is the string returned
    :param [<int:type>] The type of query (Ie, `QtWidgets.QMessageBox.Information` / `QtWidgets.QMessageBox.Warning`)
    :return <str:result> The query result - this is the string displayed on the chosen button
    """
    mb = QtWidgets.QMessageBox()
    mb.setIcon(type_)
    mb.setWindowIcon(QtGui.QIcon(juniper.engine.resources.default_icon_path()))
    mb.setText(description)
    mb.setWindowTitle(title)

    if(len(options) > 4):
        raise AttributeError(f"`options` parameter can only have a max of 4 options. Got {len(options)}!\n(This may be fixed in a later version.)")

    option_keys = [
        QtWidgets.QMessageBox.Yes,
        QtWidgets.QMessageBox.YesAll,
        QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.NoAll,
    ]

    standard_buttons = 0
    for i in range(len(options)):
        option = options[i]
        key = option_keys[i]
        standard_buttons = standard_buttons | key

    mb.setStandardButtons(standard_buttons)

    for i in range(len(options)):
        option = options[i]
        key = option_keys[i]
        mb.setButtonText(key, option)

    output = options[option_keys.index(mb.exec())]
    return output

