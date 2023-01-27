"""
Menus:
    Module containing base logic for abstract menu creation.
    This module is also responsible for creating menus to launch all available Juniper tools in a range of host applications.

Tree:
    ..

Command Server:
    Module which initializes a simple command listen server for the current host.
    This can be used to send and recieve commands from external scripts and applications.
"""
import juniper
import juniper.engine.types.module


class JuniperInterface(juniper.engine.types.module.Module):
    def on_startup(self):
        import juniper
        import juniper.runtime.widgets

        # Juniper Menus
        import juniper.interface.menus.juniper_menu
        juniper.interface.menus.juniper_menu.JuniperMenu()

        # Standalone module which creates a custom widget, which displays various tools under different groups.
        # For Qt based applications, this also includes docking within the application.
        # For non Qt based applications, this is created as a floating dialog.
        import juniper.interface.tree
        juniper.interface.tree.JuniperTreeManager().create_tree()

        # Command Server

        import juniper.interface.command_server
        from juniper.interface.command_server import command_server

        if(juniper.program_context not in ["python"]):
            juniper.runtime.widgets.get_application()  # command server uses Qt tick - ensure QApplication is initialized
            command_server.CommandServer()

    def on_post_startup(self):
        if(juniper.program_context == "max"):
            # This is a hacky workaround to adding in a Qt based menu on Max startup
            # it seems like the security changes now remove any python/maxscript menus added during the base startup initialization
            # this defers it until post startup via a maxscript timer which is hit off a instantly after the whole startup
            # process is complete.
            import pymxs
            import qtmax
            pymxs.runtime.execute("global forceMenuRollout")
            toolbar = qtmax.GetQMaxMainWindow().menuBar()
            for i in pymxs.runtime.g_juniperMenus:
                toolbar.addMenu(i)

    def on_tick(self):
        import juniper.interface.command_server.command_server
        juniper.interface.command_server.command_server.CommandServer().tick()
