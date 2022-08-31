"""
Custom module which initializes a simple command listen server for the current host.
This can be used to send and recieve commands from external scripts and applications.
"""
import juniper.engine.types.module


class CommandServer(juniper.engine.types.module.Module):
    def on_startup(self):
        import juniper
        import juniper.widgets

        import juniper_process.command_server
        from juniper_process.command_server import command_server

        if(juniper.program_context not in ["python"]):
            juniper.widgets.get_application()  # command server uses Qt tick - ensure QApplication is initialized
            port = juniper_process.command_server.listen_port(juniper.program_context)
            command_server.CommandServer(port)
