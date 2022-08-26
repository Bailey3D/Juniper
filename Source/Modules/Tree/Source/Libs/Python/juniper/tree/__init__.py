"""
"""
import os
import json
from collections import OrderedDict
from qtpy import QtWidgets, QtGui, QtCore

import juniper
import juniper.decorators
import juniper.engine
import juniper.engine.logging
import juniper.types.framework.singleton
import juniper.types.math.color
import juniper.utilities.json as json_utils
import juniper.widgets.q_dock_widget_wrapper

from juniper.tree.widgets import q_juniper_tree
from juniper.tree.config_manager import ConfigManager


log = juniper.engine.logging.Log(plugin="Juniper Tree")
groups_colour = juniper.types.math.color.Color(0.0, 0.0, 0.0, 0.05)


def juniper_tree_user_config_path():
    output = os.path.join(
        juniper.paths.root(),
        "Cached\\UserConfig\\juniper_tree.json"
    )

    if(not os.path.isfile(output)):
        if(not os.path.isdir(os.path.dirname(output))):
            os.makedirs(os.path.dirname(output))
        with open(output, "w") as f:
            json.dump({}, f)

    return output


class JuniperTree(object):
    def __init__(self):

        if(not os.path.isdir(os.path.dirname(juniper_tree_user_config_path()))):
            os.makedirs(os.path.dirname(juniper_tree_user_config_path()))

        json_utils.set_file_property(
            juniper_tree_user_config_path(),
            f"programs.{juniper.program_context}.enabled",
            True
        )

        self.q_juniper_tree_widget = q_juniper_tree.QJuniperTreeWidget()
        self.q_juniper_tree = juniper.widgets.q_dock_widget_wrapper.create_dock_widget(
            self.q_juniper_tree_widget,
            identifier="juniper.juniper_tree",
            title="Juniper Tree",
            minimum_width=ConfigManager().default_width,
            allowed_areas=(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea),
            features=(QtWidgets.QDockWidget.DockWidgetClosable | QtWidgets.QDockWidget.DockWidgetFloatable),
            stylesheet="QDockWidget > QWidget{border:1px solid rgba(0, 0, 0, 50);}",
            close_event=self.closeEvent
        )

        all_macros = juniper.engine.JuniperEngine().tools

        # sort into categories alphabetically (juniper first)
        macros_categories = {}
        for script in all_macros:
            if(script.parent_category not in macros_categories):
                macros_categories[script.parent_category] = [script]
            else:
                macros_categories[script.parent_category].append(script)
        macros_categories = OrderedDict(sorted(macros_categories.items()))
        if("Juniper" in macros_categories):
            macros_categories.move_to_end("Juniper", last=False)

        # sort categories into groups alphabetically
        macros_groups_sorted = {}

        for category in macros_categories:
            group_data = {}

            for macro in macros_categories[category]:
                if(macro.group not in group_data):
                    group_data[macro.group] = [macro]
                else:
                    group_data[macro.group].append(macro)
            group_data = OrderedDict(sorted(group_data.items()))

            # sort groups by macro alphabetically (no group first)
            for group in group_data:
                group_data[group] = sorted(group_data[group], key=lambda x: x.display_name.lower())

            macros_groups_sorted[category] = group_data

        # Groups
        for category in macros_groups_sorted:
            category_groups = macros_groups_sorted[category]
            for group in category_groups:
                group_macros = category_groups[group]

                for macro in group_macros:
                    if(macro.group != ""):
                        category_widget = self.q_juniper_tree_widget.add_category_widget(macro.parent_category)

                        if(macro.group and macro.group != "Core"):
                            group_widget = category_widget.add_group(macro.group)
                        else:
                            group_widget = category_widget

                        button_class = (
                            QtWidgets.QToolButton if
                            (macro.icon_path and os.path.isfile(macro.icon_path)) else
                            QtWidgets.QPushButton
                        )

                        macro_button = button_class()
                        macro_button.setText(macro.display_name)
                        macro_button.setToolTip(macro.summary)
                        macro_button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
                        macro_button.setFixedHeight(ConfigManager().button_height)
                        macro_button.clicked.connect(macro.run)

                        # for rendering in the group / titlebar
                        if(macro.group == "Core"):
                            macro_button.setText("")
                            category_widget.add_titlebar_widget(macro_button)

                        # regular button add
                        else:
                            group_widget.addWidget(macro_button)

                        macro_button.setStyleSheet(f"""
                            {button_class.__name__}{{
                                background-color:rgba(0, 0, 0, 0);
                                border:none;
                                text-align: left;
                            }}
                            {button_class.__name__}::hover{{2022
                                background-color:rgba(0, 0, 0, 10%);
                                border:none;
                                text-align: left;
                            }}
                        """)

                        if(macro.icon_path and os.path.isfile(macro.icon_path)):
                            macro_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
                            macro_button.setIcon(QtGui.QIcon(macro.icon_path))

    def closeEvent(self, event):
        json_utils.set_file_property(
            juniper_tree_user_config_path(),
            f"programs.{juniper.program_context}.enabled",
            False
        )


class JuniperTreeManager(object, metaclass=juniper.types.framework.singleton.Singleton):
    def __init__(self):
        self.juniper_tree = None

    @property
    def is_enabled(self):
        output = json_utils.get_property(
            juniper_tree_user_config_path(),
            f"programs.{juniper.program_context}.enabled"
        ) is True
        output = output and juniper.program_context not in ("python",)
        return output

    def create_tree(self, force=False):
        if(force or self.is_enabled):
            self.juniper_tree = JuniperTree()
        return self.juniper_tree

    def add_tool_widget(self, tool_name, widget):
        if(self.juniper_tree):
            category_widget = self.juniper_tree.q_juniper_tree_widget.add_category_widget(tool_name, tab_content=False, tint=groups_colour)
            category_widget.addWidget(widget)
