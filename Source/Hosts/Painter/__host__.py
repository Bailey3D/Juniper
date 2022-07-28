"""
Base implementation for Juniper support in Substance Painter
"""
import os

import juniper.engine


class Painter(juniper.engine.JuniperEngine):
    def on_startup(self):
        """
        Adds the `substance_painter.juniper` module to `substance_painter.__path__`
        """
        import substance_painter
        substance_painter.__path__.append(
            os.path.join(self.workspace_root, "Source\\Hosts\\Painter\\Source\\Libs\\Python\\substance_painter")
        )

    def on_install(self):
        """
        Installs the Juniper bootstrap to Substance Painter startup
        """
        bootstrap_path = os.path.join(
            juniper.paths.documents(),
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