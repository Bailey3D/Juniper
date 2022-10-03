"""
:type script
:callbacks [startup]
:desc Initializes the JuniperHub application in the system tray
"""
import juniper.widgets
import juniper_hub.juniper_hub
import juniper_hub.hub_finder


app = juniper.widgets.get_application()
juniper_hub.hub_finder.find_and_close()
juniper_hub.juniper_hub.JuniperHub()
