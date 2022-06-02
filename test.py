'''import sys
sys.argv.append("juniper:program_context=juniper_hub")

import juniper
import juniper.widgets
import juniper_hub.juniper_hub
import juniper_hub.hub_finder



app = juniper.widgets.get_application()
juniper_hub.hub_finder.find_and_close()
tray = juniper_hub.juniper_hub.JuniperHub()
sys.exit(app.exec_())
'''
import juniper
import juniper_designer


juniper_designer.add_shelf("", "")
print("Done!")