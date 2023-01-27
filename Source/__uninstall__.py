"""
:type uninstaller
:desc Uninstalls Juniper from all known hosts
"""
import sys

# Startup in Python context to get all hosts
sys.argv.append("juniper:uninstall=true")
sys.argv.append("juniper:tick=false")
sys.argv.append("juniper:program_context=python")

import juniper
import juniper.engine


juniper.engine.JuniperEngine(bootstrap=True)


print("Juniper: Uninstalled")
