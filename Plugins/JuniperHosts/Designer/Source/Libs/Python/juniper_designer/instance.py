import os
import sd


context = sd.getContext()
application = context.getSDApplication()
package_manager = application.getPackageMgr()
ui_manager = application.getQtForPythonUIMgr()


def get_current_graph():
    """Returns the currently opened graph"""
    return ui_manager.getCurrentGraph()


def get_current_graph_selection():
    """Returns the currently selected nodes in the opened graph"""
    return ui_manager.getCurrentGraphSelection()


def get_current_package():
    """Returns the currently opened package"""
    if(get_current_graph()):
        return get_current_graph().getPackage()
    None


def get_current_package_path():
    """Returns the file path to the currently opened package"""
    if(get_current_package()):
        return get_current_package().getFilePath()
    return None


def get_package_name(package):
    """Returns the name of an input package"""
    if(package):
        return os.path.basename(package.getFilePath()).split(".")[0]
    return ""


def get_current_package_name():
    """Returns the name of the currently opened package"""
    if(get_current_package_path()):
        return os.path.basename(get_current_package_path()).split(".")[0]
    return ""


def load_sbs(path):
    """Opens an SBS in Designer from an input path"""
    if((os.path.isfile(path)) and (path.endswith(".sbs"))):
        sd_package = package_manager.loadUserPackage(path.replace("\\", "/"), True, True)
        return sd_package
    return None


def get_main_qt_window():
    app = sd.getContext().getSDApplication()
    uiMgr = app.getQtForPythonUIMgr()
    return uiMgr.getMainWindow()
