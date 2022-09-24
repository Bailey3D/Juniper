"""
:type script
:desc Binds the Qt event system to the blender event system
:callbacks [pre_startup]
:TODO! Move this to the engine override tick
"""
import bpy
from qtpy import QtCore

import juniper.engine.types.plugin
import juniper.widgets


class MainLoopHook(bpy.types.Operator):
    bl_idname = "screen.juniper_qt_mainloop"
    bl_label = "Juniper Qt Main Loop"

    def __init__(self):
        self.event_loop = None

    def register(self):
        pass

    def modal(self, context, event):
        self.event_loop.processEvents()
        juniper.widgets.get_application().sendPostedEvents(None, 0)

    def execute(self, context):
        juniper.widgets.get_application()  # initialize the QApplication
        self.event_loop = QtCore.QEventLoop()

        wm = context.window_manager
        self.timer = wm.event_timer_add(1 / 30, window=context.window)
        context.window_manager.modal_handler_add(self)


def register():
    bpy.utils.register_class(MainLoopHook)
