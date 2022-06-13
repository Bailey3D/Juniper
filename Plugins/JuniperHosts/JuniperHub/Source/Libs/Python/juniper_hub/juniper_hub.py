import os
from qtpy import QtWidgets, QtGui, QtCore

import juniper
import juniper.paths
import juniper.types.framework.singleton


class JuniperHub(metaclass=juniper.types.framework.singleton.Singleton):
    def __init__(self):
        self.parent_widget = QtWidgets.QWidget()

        self.system_tray_widget = QtWidgets.QSystemTrayIcon(self.app_icon, self.parent_widget)
        self.system_tray_widget.activated.connect(self.on_activated)
        self.system_tray_widget.setToolTip("Juniper Hub")

        self.menu = QtWidgets.QMenu(self.parent_widget)
        #self.quit_action = self.menu.addAction("Quit")
        self.system_tray_widget.setContextMenu(self.menu)
        #self.quit_action.triggered.connect(self.shutdown)

        self.system_tray_widget.show()

    '''@property
    def title(self):
        try:
            for i in sys.argv:
                i = str(i)
                if(i.startswith("title=")):
                    return i.split("=")[1]
        except Exception as e:
            pass
            #juniper.log.error(str(e))
        return "Juniper Hub"'''

    @property
    def app_icon(self):
        return QtGui.QIcon(os.path.join(juniper.paths.root(), "Resources\\Icons\\Standard\\app_default.ico"))

    def on_activated(self, event):
        if(event == QtWidgets.QSystemTrayIcon.Trigger):
            import juniper.types.framework.script
            juniper.types.framework.script.ScriptManager().find("open_git_repo").run()

    def shutdown(self):
        QtCore.QCoreApplication.exit()
