"""
:todo~ Logic here is pretty messy and hard to follow. Need to abstract out some parts.
"""
import textwrap

import juniper
import juniper.engine
import juniper.engine.types.plugin
import juniper.types.framework.script
import juniper.types.framework.singleton
import juniper.utilities.string as string_utils
import juniper.widgets.q_menu_wrapper


class __MenuGroup(object):
    def __init__(self, group_name):
        self.group_name = group_name
        self.macros = []
        self.additional_macros_grouped = {}
        self.core_macros = []

    def add_macro(self, macro):
        if(macro not in self.macros):
            self.macros.append(macro)

    def add_core_macro(self, macro):
        if(macro not in self.core_macros):
            self.core_macros.append(macro)

    def add_grouped_macro(self, macro, macro_group):
        if(macro_group not in self.additional_macros_grouped):
            self.additional_macros_grouped[macro_group] = []
        if(macro not in self.additional_macros_grouped[macro_group]):
            self.additional_macros_grouped[macro_group].append(macro)


class JuniperMenu(metaclass=juniper.types.framework.singleton.Singleton):
    def __init__(self):
        self.program_context = juniper.program_context

        #
        self.supported_hosts = [
            "blender",
            "designer",
            "juniper_hub",
            "max",
            "painter",
            "unreal",
        ]

        if(juniper.program_context in self.supported_hosts):
            #self.menu_object = juniper.widgets.q_menu_wrapper.QMenuWrapper("juniper", "Juniper")
            #self.menu = self.menu_object.menu_object
            #self.menus = [self.menu]
            self.menus = []

            engine = juniper.engine.JuniperEngine()

            menu_groups = {
                "Juniper": []  # Add "Juniper" first to ensure the menu is added first
            }

            for i in engine.tools:
                top_level_group = i.category.split("|")[0]
                if(top_level_group not in menu_groups):
                    menu_groups[top_level_group] = []
                menu_groups[top_level_group].append(i)

            for i in menu_groups:
                menu_object = juniper.widgets.q_menu_wrapper.QMenuWrapper(i, i)
                menu = menu_object.menu_object
                self.menus.append(menu)

                # 1) Integrated
                integrated_scripts = []
                for script in menu_groups[i]:
                    if(not script.is_core and script.integration_type != "separate"):
                        integrated_scripts.append(script)
                integrated_scripts_sorted = sorted(integrated_scripts, key=lambda x: x.category + "|z_" + x.display_name)
                self.append_menu(menu, branches=None, macros=integrated_scripts_sorted)

                # 2) Separate
                separate_scripts = []
                for script in menu_groups[i]:
                    if(script.integration_type == "separate" and not script.is_core):
                        separate_scripts.append(script)
                separate_scripts_sorted = sorted(separate_scripts, key=lambda x: x.category + "|z_" + x.display_name)
                if(len(separate_scripts_sorted)):
                    menu_object.add_separator()
                self.append_menu(menu, branches=None, macros=separate_scripts_sorted)

                # 3) Core
                core_scripts = []
                for script in menu_groups[i]:
                    if(script.is_core):
                        core_scripts.append(script)
                core_scripts_sorted = sorted(core_scripts, key=lambda x: "z|z_" + x.display_name)
                if(len(core_scripts_sorted)):
                    menu_object.add_separator()
                self.append_menu(menu, branches=None, macros=core_scripts_sorted)

            #
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

        if(self.program_context not in ["unreal", "blender"]):
            action = parent.addAction(macro.display_name)
            action.triggered.connect(macro.run)
            action.setToolTip(macro.summary)
        elif(self.program_context == "blender"):
            pass  # TODO! Blender: Actions for blender menus
        elif(self.program_context == "unreal"):
            # TODO~ There's some issue with the unreal menu builder which messes up the order of 
            # adding actions
            import unreal
            action = unreal.ToolMenuEntry(
                name=macro.display_name,
                type=unreal.MultiBlockType.MENU_ENTRY,
                insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
            )
            action.set_label(string_utils.snake_to_name(macro.display_name))
            command_string = textwrap.dedent(f"""
                import juniper.engine
                script = juniper.engine.JuniperEngine().find_tool("{macro.name}")
                if(script):
                    script.run()
            """)
            action.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                "None",
                string=command_string)
            parent.add_menu_entry("Juniper", action)
        return action

    def append_menu(self, parent, branches=None, macros=[]):
        """Add a list of macros to the menu
        :param [<dict:branches>] Current branches dict
        :param [<[Macros]:macros>] The macros to add
        """
        if(self.program_context == "blender"):  # TODO!
            return {"_menu":parent}
        if(not branches):
            branches = {"_menu": parent}

        for macro in macros:
            prev_key = branches

            if(macro.is_core):
                base_category = ""
            else:
                base_category = macro.category.split("|", 1)[1]

            category_split = base_category.split("|")
            for subcategory in category_split:
                display_name = string_utils.snake_to_name(subcategory)

                if(subcategory != ""):
                    if(subcategory not in prev_key):

                        if(self.program_context == "unreal"):
                            # Unreal is non-qt based
                            prev_key[subcategory] = {"_menu": prev_key["_menu"].add_sub_menu("Tools", subcategory, display_name, display_name)}
                        else:
                            # Qt based menus
                            prev_key[subcategory] = {"_menu": prev_key["_menu"].addMenu(display_name)}

                    prev_key = prev_key[subcategory]

                # add tool
                if(subcategory == category_split[-1]):
                    if("_macros" not in prev_key):
                        prev_key["_macros"] = [macro]
                    else:
                        prev_key["_macros"].append(macro)

                    self.add_action(prev_key["_menu"], macro)

        return branches
