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
        bootstrap_path = os.path.join(
            juniper.paths.documents(),
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
