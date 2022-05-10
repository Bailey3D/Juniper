import juniper_globals
program_context = juniper_globals.get("program_context")

import sys


def initialize_log():
    import juniper.framework.logging
    log = juniper.framework.logging.Log(plugin="Juniper")
    setattr(sys.modules[__name__], "log", log)
