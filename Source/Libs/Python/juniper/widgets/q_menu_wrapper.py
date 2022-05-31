"""
DCC Specific menu object.
- For applications which use Qt this will wrap QMenu
- For other programs which we are able to wrap, this will wrap the program specific object
- For programs which have no exposure, this will be empty / logicless
"""
from qtpy import QtWidgets

import juniper
import juniper.decorators


class QMenuWrapper(object):
    def __init__(self, name, display_name):
        """
        Top level menu object wrapper
        :param <str:name> Code name of the menu
        :param <str:display_name> Friendly / display name of the menu
        :return <object:menu> Menu object, type can change depending on the host application
        """
        self.menu_object = None
        self.name = name
        self.display_name = display_name
        self.__initialize_menu()

    @juniper.decorators.virtual_method
    def __initialize_menu(self):
        raise NotImplementedError

    @__initialize_menu.override("painter")
    def _initialize_menu(self):
        import substance_painter.ui
        menu = QtWidgets.QMenu(self.display_name, None)
        menu.setToolTipsVisible(True)
        menu.setObjectName(self.display_name)
        substance_painter.ui.add_menu(menu)
        self.menu_object = menu

    @__initialize_menu.override("designer")
    def _initialize_menu(self):
        import sd
        uimgr = sd.getContext().getSDApplication().getQtForPythonUIMgr()
        menu = QtWidgets.QMenu(self.name, None)
        menu.setToolTipsVisible(True)
        menu.setObjectName(self.display_name)
        uimgr.newMenu(self.display_name, self.name)
        self.menu_object = uimgr.findMenuFromObjectName(self.name)

    @__initialize_menu.override("ue4")
    def _initialize_menu(self):
        import unreal
        menus = unreal.ToolMenus.get()
        main_menu = menus.find_menu("LevelEditor.MainMenu")
        juniper_menu = main_menu.add_sub_menu(main_menu.get_name(), self.display_name, self.display_name, self.display_name)
        juniper_menu.searchable = True
        menus.refresh_all_widgets()
        self.menu_object = juniper_menu

    @__initialize_menu.override("max")
    def _initialize_menu(self):
        import qtmax
        toolbar = qtmax.GetQMaxMainWindow()

        for i in list(toolbar.menuBar().actions()):
            if(i.text() == "Juniper"):
                toolbar.menuBar().removeAction(i)

        main_menu = QtWidgets.QMenu(self.display_name, toolbar)
        main_menu.setToolTipsVisible(True)
        main_menu.setObjectName(self.name)
        toolbar.menuBar().addMenu(main_menu)
        self.menu_object = main_menu

    # ----------------------------------------------------------------

    @juniper.decorators.virtual_method
    def add_separator(self):
        """Add a separator to the menu"""
        if(self.menu_object):
            self.menu_object.addSeparator()

    @add_separator.override("ue4")
    def _add_separator(self):
        import unreal
        action = unreal.ToolMenuEntry(
            type=unreal.MultiBlockType.SEPARATOR,
            insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT))
        self.menu_object.add_menu_entry("Juniper", action)
