import juniper.engine.decorators


@juniper.engine.decorators.program_context("max")
def get_maxscript_listener_hwnd():
    """Gets the window handle for the maxscript listener
    :return <int:hwnd> The window handle
    """
    import pymxs
    return pymxs.runtime.windows.getchildhwnd(0, "MAXScript Listener")[0]


@juniper.engine.decorators.program_context("max")
def open_listener():
    """Opens the maxscript listener"""
    import pymxs
    pymxs.runtime.actionMan.executeAction(0, "40472")


@juniper.engine.decorators.program_context("max")
def close_listener():
    """Closes the maxscript listener"""
    import pymxs
    pymxs.runtime.uiaccessor.closedialog(get_maxscript_listener_hwnd())
