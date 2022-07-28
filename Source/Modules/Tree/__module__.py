"""
Standalone module which creates a custom widget, which displays various tools under different groups.
For Qt based applications, this also includes docking within the application.
For non Qt based applications, this is created as a floating dialog.
"""
import juniper.engine.types.module


class Tree(juniper.engine.types.module.Module):
    def on_startup(self):
        import juniper.tree

        juniper.tree.JuniperTreeManager().create_tree()
