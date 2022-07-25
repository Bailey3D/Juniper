"""
:type script
:callbacks [startup]
:desc Initializes the juniper tree widget/tool for the current DCC
"""
import juniper_tree


juniper_tree.JuniperTreeManager().create_tree()
