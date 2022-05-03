import juniper
import juniper_tree
import juniper.widgets as qt_utils

import juniper


app = qt_utils.get_application()
juniper_tree.JuniperTreeManager.create_tree(force=True)

if(juniper.program_context in ("standalone", "python")):
    app.exec_()
