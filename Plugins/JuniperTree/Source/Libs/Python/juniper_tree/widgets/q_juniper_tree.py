from qtpy import QtWidgets, QtCore

from juniper.widgets import q_v_scroll_layout

from juniper_tree.widgets import q_tree_group
from juniper_tree.config_manager import ConfigManager
from juniper.framework.tooling.macro import MacroManager


class QJuniperTreeWidget(QtWidgets.QWidget):
    def __init__(self):
        super(QJuniperTreeWidget, self).__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # base properties
        self.__initialized = False
        self.__width = ConfigManager.default_width
        self.__default_columns = ConfigManager.default_columns  # may need to functionize if adding in compact mode

        #
        self.__child_widgets = []
        self.__categories = {}

        self.__build_base_ui()

    def __build_base_ui(self):
        """Builds the base UI for the hub"""
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(self.__width)
        self.setMinimumHeight(750)

        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setMargin(0)
        self.central_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.central_layout)

        self.content_layout_outer = q_v_scroll_layout.QVScrollLayout(show_scroll_handles=False)
        self.content_layout_outer.setSpacing(0)
        self.content_layout_outer.setContentsMargins(0, 0, 0, 0)
        self.content_layout_outer.setMargin(0)
        self.content_layout_outer.setAlignment(QtCore.Qt.AlignTop)
        self.central_layout.addLayout(self.content_layout_outer)

        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setAlignment(QtCore.Qt.AlignTop)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setMargin(0)
        self.content_layout.setSpacing(0)
        self.content_layout_outer.addLayout(self.content_layout)

        # TODO?: Menu buttons

        # Search box
        self.q_search_list = QtWidgets.QListWidget()
        self.search_list_max_entries_visible = 16
        self.q_search_list.itemDoubleClicked.connect(self.__search_entry_clicked)
        self.central_layout.addWidget(self.q_search_list)

        # Search line edit
        self.q_search = QtWidgets.QLineEdit()
        self.q_search.setPlaceholderText("Search..")
        self.q_search.textChanged.connect(self.__update_search_entries)
        self.central_layout.addWidget(self.q_search)
        self.__update_search_entries()

    def closeEvent(self, event):
        """Event called when the juniper hub is closed"""
        for i in self.__child_widgets:
            i.setParent(None)
            i.deleteLater()
        super(QJuniperTreeWidget, self).closeEvent(event)

    def add_category_widget(self, category_name, tint=None, tab_content=True):
        """Adds a category to the content layout
        :param <str:category_name> Name of the category to add
        :return <QCollapsibleWidget:category_widget> The added category widget
        """
        if(category_name not in self.__categories):
            category_widget = q_tree_group.QHubGroup(
                category_name,
                parent=self.content_layout,
                tint=tint,
                tab_content=tab_content
            )
            self.__categories[category_name] = category_widget
        return self.__categories[category_name]

    def __update_search_entries(self, *args):
        self.q_search_list.clear()
        search_string = self.q_search.text().lower()

        if(not search_string):
            self.q_search_list.hide()
            return

        macros_to_add = []

        for macro in MacroManager.all_macros:
            if(
                search_string in macro.display_name.lower()
                or search_string in macro.name.lower()
                or search_string in macro.group.lower()
                or search_string in macro.parent_category.lower()
            ):
                macros_to_add.append(macro)

        if(len(macros_to_add)):
            macros_to_add = sorted(macros_to_add, key=lambda x: x.name.lower())
            for macro in macros_to_add:
                item = QtWidgets.QListWidgetItem(macro.display_name)
                item.setToolTip(macro.tooltip)
                setattr(item, "macro", macro)
                self.q_search_list.addItem(item)
            self.q_search_list.show()
            self.q_search_list.setFixedHeight(
                self.q_search_list.sizeHintForRow(0) * min(self.search_list_max_entries_visible, self.q_search_list.count() + 1)
            )

    def __search_entry_clicked(self, item):
        item.macro.run()
