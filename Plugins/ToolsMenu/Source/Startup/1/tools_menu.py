"""
:script
:type startup
:desc Startup script used to initialize a tools menu in the current host program
:supported ["max", "ue4", "blender", "designer", "painter"]
"""
import textwrap

import juniper
import juniper.utilities.string as string_utils
import juniper.framework.backend.plugin
import juniper.widgets.q_menu_wrapper


class ToolsMenu(object):
    def __init__(self):
        self.program_context = juniper.program_context

        self.exclude_hosts = ["houdini"]

        if(self.program_context not in self.exclude_hosts):
            self.menu_object = juniper.widgets.q_menu_wrapper.QMenuWrapper("juniper", "Juniper")
            self.menu = self.menu_object.menu_object
            self.menus = [self.menu]

            # add all "integrated" macros
            integrated_macros = set()
            for plugin in juniper.framework.backend.plugin.PluginManager():
                if(plugin.enabled and plugin.integration_type == "integrated"):
                    for macro in plugin.macros:
                        integrated_macros.add(macro)
            self.append_menu(self.menu, branches=None, macros=integrated_macros)

            # add all "separate" macros / groups
            # self.menu_object.add_separator()
            for plugin in juniper.framework.backend.plugin.PluginManager():
                if(plugin.enabled and plugin.integration_type == "separate"):
                    self.append_menu(self.menu, branches=None, macros=plugin.macros, submenu=plugin.display_name)

            # add all "standalone" macros / groups as new menus
            for plugin in juniper.framework.backend.plugin.PluginManager():
                if(plugin.enabled and plugin.integration_type == "standalone"):
                    plugin_menu = juniper.widgets.q_menu_wrapper.QMenuWrapper(plugin.name, plugin.display_name)
                    self.append_menu(plugin_menu.menu_object, branches=None, macros=plugin.macros)
                    self.menus.append(plugin_menu.menu_object)
                    if(len(plugin.core_macros)):
                        plugin_menu.add_separator()
                        for i in plugin.core_macros:
                            self.add_action(plugin_menu.menu_object, i)

            # core macros
            # TODO! Juniper should not have any base tools anymore. We need a different way to inject "core macros"
            self.menu_object.add_separator()
            '''root_module = juniper.framework.backend.module.ModuleManager.get_module("juniper")
            for i in root_module.get_core_macros():
                self.add_action(self.menu, i)'''

            if(self.program_context == "max"):
                import pymxs
                pymxs.runtime.execute("global g_juniperMenus")
                pymxs.runtime.g_juniperMenus = pymxs.runtime.array()
                for i in self.menus:
                    pymxs.runtime.append(pymxs.runtime.g_juniperMenus, i)

    def add_action(self, parent, macro):
        """Add a macro as an action to the menu
        :param <menu:parent> The parent menu object
        :param <Macro:macro> The macro to add
        """
        action = None

        if(self.program_context in ["designer", "max", "painter"]):
            action = parent.addAction(macro.display_name)
            action.triggered.connect(macro.run)
            action.setToolTip(macro.tooltip)
        elif(self.program_context == "ue4"):
            import unreal
            action = unreal.ToolMenuEntry(
                name=macro.display_name,
                type=unreal.MultiBlockType.MENU_ENTRY,
                insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
            )
            action.set_label(string_utils.snake_to_name(macro.display_name))
            command_string = textwrap.dedent("""
                import juniper.framework.tooling.macro as macro
                macro.MacroManager.run_macro(
                    "{}",
                    "{}"
                )
            """).format(macro.module if macro.module else "juniper", macro.name)
            action.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                "None",
                string=command_string)
            parent.add_menu_entry("Juniper", action)
        return action

    def append_menu(self, parent, branches=None, macros=[], submenu=None):
        """Add a list of macros to the menu
        :param [<dict:branches>] Current branches dict
        :param [<[Macros]:macros>] The macros to add
        """
        if(not branches):
            branches = {"_menu": parent}

        for macro in macros:
            prev_key = branches
            if(submenu):
                base_category = submenu + "|" + macro.category
            else:
                base_category = macro.category
            category_split = base_category.split("|")
            category_split = category_split[-1:] if category_split[0] == "juniper" else category_split
            for subcategory in category_split:
                display_name = string_utils.snake_to_name(subcategory)

                if(subcategory not in prev_key):

                    if(self.program_context in ["designer", "max", "painter"]):
                        prev_key[subcategory] = {"_menu": prev_key["_menu"].addMenu(display_name)}
                    elif(self.program_context == "ue4"):
                        prev_key[subcategory] = {"_menu": prev_key["_menu"].add_sub_menu("Tools", subcategory, display_name, display_name)}

                prev_key = prev_key[subcategory]

                # add tool
                if(subcategory == category_split[-1]):
                    if("_macros" not in prev_key):
                        prev_key["_macros"] = [macro]
                    else:
                        prev_key["_macros"].append(macro)

                    self.add_action(prev_key["_menu"], macro)


if(juniper.program_context != "python"):
    tm = ToolsMenu()
