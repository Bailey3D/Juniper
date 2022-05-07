import sys

import juniper.framework.logging

import juniper_globals


program_context = juniper_globals.get("program_context")

log = juniper.framework.logging.Log(plugin="Juniper")
setattr(sys.modules[__name__], "log", log)
