'''import sys
sys.argv.append("juniper:install=true")
sys.argv.append("juniper:startup=true")
sys.argv.append("juniper:program_context=python")

import juniper
import juniper.engine
import juniper.engine.bootstrap
juniper.engine.JuniperEngine().shutdown()


for i in juniper.engine.JuniperEngine().supported_hosts:
    sys.argv.append("juniper:install=true")
    sys.argv.append("juniper:startup=false")
    sys.argv.append(f"juniper:program_context={i}")
    juniper.engine.bootstrap.Bootstrap()
    engine = juniper.engine.JuniperEngine()
    print(engine)
    engine.shutdown()
'''
import juniper
print("Done")