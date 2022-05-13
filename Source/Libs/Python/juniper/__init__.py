import juniper_globals
program_context = juniper_globals.get("program_context")

import sys


def initialize_log():
    import juniper.framework.logging
    log = juniper.framework.logging.Log(plugin="Juniper")
    setattr(sys.modules[__name__], "log", log)


def supported_hosts():
    """
    :return <[str]:hosts> The names of all supported hosts (in the "Plugins\\JuniperHosts\\" directory)
    """
    import juniper.plugins
    output = []
    for i in juniper.plugins.PluginManager():
        if(i.is_host_plugin):
            output.append(i.name)
    return sorted(output)
