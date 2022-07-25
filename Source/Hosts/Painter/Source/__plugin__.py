import os

import juniper.engine


class Painter(juniper.engine.JuniperEngine):
    def on_startup(self):
        import substance_painter
        substance_painter.__path__.append(
            os.path.join(self.workspace_root, "Source\\Hosts\\Painter\\Source\\Libs\\Python\\substance_painter")
        )

    def on_install(self):
        bootstrap_path = os.path.join(
            juniper.paths.documents(),
            "Allegorithmic\\Substance Painter\\python", "startup\\__juniper_startup__.py"
        )
        self.create_bootstrap_file(bootstrap_path)

    def on_shutdown(self):
        pass

    def bootstrap_call_lines(self):
        return [
            "def start_plugin():",
            "    Bootstrap()"
        ]