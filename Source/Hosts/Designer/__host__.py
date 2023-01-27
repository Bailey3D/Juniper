"""
Base implementation for Juniper support in Substance Designer
"""
import os

import juniper.engine


class Designer(juniper.engine.JuniperEngine):

    def get_host_module_names(self):
        return ("sd",)

    def on_install(self):
        """
        Installs the Juniper bootstrap to Substance Designer
        """
        import juniper.utilities.os.windows.paths
        bootstrap_path = os.path.join(
            juniper.utilities.os.windows.paths.documents(),
            "Allegorithmic\\Substance Designer\\python\\sduserplugins\\__juniper_startup__.py"
        )
        self.create_bootstrap_file(bootstrap_path)

    def bootstrap_call_lines(self):
        """
        Substance Designer requires specific methods for startup/shutdown of plugins
        """
        return [
            "def initializeSDPlugin():",
            "    Bootstrap()",
            "def uninitializeSDPlugin():",
            "    pass"
        ]

    def get_main_window(self):
        import sd.juniper.instance
        return sd.juniper.instance.get_main_qt_window()

    def create_qt_dock_widget(self, child_widget, identifier="", title="Dock"):
        import sd
        from qtpy import QtWidgets
        ui_mgr = sd.getContext().getSDApplication().getQtForPythonUIMgr()
        output = ui_mgr.newDockWidget(identifier, title)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        output.setLayout(main_layout)
        main_layout.addWidget(child_widget)
        return output
