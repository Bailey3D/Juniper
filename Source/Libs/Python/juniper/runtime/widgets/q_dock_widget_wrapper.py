"""
Wrappers / helpers for Dock Widgets in the different host Contexts
"""
from qtpy import QtWidgets, QtCore

import juniper.runtime.widgets
import juniper.engine


def create_dock_widget(
    child_widget, identifier="", title="Dock", minimum_width=None,
    allowed_areas=None, features=None, stylesheet=None, close_event=None
):
    """
    Adds a Qt based dock widget to the current application (Qt support dependent)
    :param <QWidget:child_widget> The widget to add to the dock
    :param [<str:identifier>] Code name identifier for this dock
    :param [<str:title>] The friendly title of this dock
    :param [<int:minimum_width>] The minimum width allowed for this dock
    :param [<int:allowed_areas>] Allowed areas for this dock, Ie `QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea`
    :param [<int:features>] Features of this dock, Ie `QtWidgets.QDockWidget.DockWidgetClosable | QtWidgets.QDockWidget.DockWidgetFloatable`
    :param [<str:stylesheet>] Stylesheet override for this widget
    :param [<function:close_event>] Optional override function called on this dock's close event
    """
    main_window = juniper.runtime.widgets.get_main_window()
    output = juniper.engine.JuniperEngine().create_qt_dock_widget(
        child_widget,
        identifier=identifier,
        title=title
    )

    if(close_event):
        setattr(output, "nativeCloseEvent", output.closeEvent)
        setattr(output, "overrideCloseEvent", close_event)

        def __closeEventWrapper(event):
            output.overrideCloseEvent(event)
            output.nativeCloseEvent(event)
        output.closeEvent = __closeEventWrapper

    output.setWindowTitle(title)
    output.setObjectName(identifier)

    if(isinstance(output, QtWidgets.QDockWidget) and main_window):

        main_window.setDockNestingEnabled(True)
        main_window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, output)

        for i in main_window.findChildren(QtWidgets.QDockWidget):
            is_left = main_window.dockWidgetArea(i) == QtCore.Qt.LeftDockWidgetArea
            not_viewport = "viewport" not in i.windowTitle().lower()
            is_this_dock_type = i.windowTitle() == output.windowTitle()
            is_not_self = i is not output

            if(i is not output):
                if(is_this_dock_type and is_not_self):
                    i.setParent(None)
                else:  # get already docked on left and split with this
                    if(is_left and not_viewport):
                        main_window.splitDockWidget(
                            output,
                            i,
                            QtCore.Qt.Horizontal
                        )

        if(allowed_areas is not None):
            output.setAllowedAreas(allowed_areas)
        if(features is not None):
            output.setFeatures(features)

    if(minimum_width):
        output.setMinimumWidth(minimum_width)
    if(stylesheet):
        output.setStyleSheet(stylesheet)

    # for non Qt based applications we still render the widget
    # just as a floating dock instead
    output.show()
    juniper.runtime.widgets.initialize_host_window_parenting(output)

    return output
