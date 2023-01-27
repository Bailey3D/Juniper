"""
:type installer
:desc Installs Juniper for all known hosts
"""
import sys

# Startup in Python context to get all hosts
sys.argv.append("juniper:install=true")
sys.argv.append("juniper:startup=true")
sys.argv.append("juniper:tick=false")
sys.argv.append("juniper:program_context=python")


import juniper
import juniper.engine
import juniper.bootstrap


juniper.engine.JuniperEngine().shutdown()

# Loop all hosts and install
for i in juniper.engine.JuniperEngine().supported_hosts:
    print(f"Juniper: Installing For Host {i}")
    sys.argv.append("juniper:install=true")
    sys.argv.append("juniper:startup=false")
    sys.argv.append("juniper:tick=false")
    sys.argv.append(f"juniper:program_context={i}")
    bootstrap = juniper.bootstrap.Bootstrap()
    engine = juniper.engine.JuniperEngine()
    engine.shutdown()
    print("---")
