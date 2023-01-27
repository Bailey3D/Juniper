"""
:type tool
:category Interface
:summary Launches the Juniper Tree as a standalone app
:icon icons\\standard\\app_default.png
"""
import juniper.interface.tree
import juniper.runtime.widgets as qt_utils

import juniper


app = qt_utils.get_application()
juniper.interface.tree.JuniperTreeManager().create_tree(force=True)

if(juniper.program_context in ("python",)):
    app.exec_()
