import pymxs.juniper.sdk


def disable_macro_recorder():
    """
    Disables the 3DS Max macro recorder
    """
    core_interface = pymxs.juniper.sdk.GetCOREInterface()
    core_interface.MacroRecorder.Disable()


def enable_macro_recorder():
    """
    Disables the 3DS Max macro recorder
    """
    core_interface = pymxs.juniper.sdk.GetCOREInterface()
    core_interface.MacroRecorder.Enable()
