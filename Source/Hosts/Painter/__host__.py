"""
Base implementation for Juniper support in Substance Painter
"""
import os

import juniper.engine


class Painter(juniper.engine.JuniperEngine):
    def get_host_module_names(self):
        return ("substance_painter",)

    def on_install(self):
        """
        Installs the Juniper bootstrap to Substance Painter startup
        """
        import juniper.utilities.os.windows.paths
        bootstrap_path = os.path.join(
            juniper.utilities.os.windows.paths.documents(),
            "Allegorithmic\\Substance Painter\\python", "startup\\__juniper_startup__.py"
        )
        self.create_bootstrap_file(bootstrap_path)

    def bootstrap_call_lines(self):
        """
        Substance Painter requires a specific method to initialize plugins.
        """
        return [
            "def start_plugin():",
            "    Bootstrap()"
        ]

    def get_main_window(self):
        import substance_painter.ui
        return substance_painter.ui.get_main_window()

    def create_qt_dock_widget(self, child_widget, identifier="", title="Dock"):
        import substance_painter.ui
        output = substance_painter.ui.add_dock_widget(child_widget)
        output.setWindowTitle(title)
        return output
