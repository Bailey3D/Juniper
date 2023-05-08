print(1)
import juniper
import juniper.engine.types.plugin
import bailey3d
print(2)

for i in juniper.engine.types.plugin.PluginManager():
    print(i.name)
    print(bool(i))
    print("---")
