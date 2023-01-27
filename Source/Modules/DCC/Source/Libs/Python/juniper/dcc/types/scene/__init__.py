import os
import subprocess

import juniper.dcc.types.scene.node
import juniper.dcc.types.scene.selection_set
import juniper.engine.decorators
import juniper.utilities.pathing
import juniper.runtime.types.framework.singleton


class SceneManager(metaclass=juniper.runtime.types.framework.singleton.Singleton):
    def __init__(self):
        pass

    @property
    def current_scene_path(self):
        return self.get_current_scene_path()

    @juniper.engine.decorators.virtual_method
    def get_current_scene_path(self):
        raise NotImplementedError

    @get_current_scene_path.override("blender")
    def get_current_scene_path(self):
        import bpy
        return bpy.data.filepath

    @get_current_scene_path.override("designer")
    def get_current_scene_path(self):
        import sd
        uimgr = sd.getContext().getSDApplication().getQtForPythonUIMgr()
        return uimgr.getCurrentGraph().getPackage().getFilePath()

    @get_current_scene_path.override("max")
    def get_current_scene_path(self):
        import pymxs
        return os.path.join(pymxs.runtime.maxFilePath, pymxs.runtime.maxFileName)

    @get_current_scene_path.override("painter")
    def get_current_scene_path(self):
        import substance_painter.project
        try:
            output = substance_painter.project.file_path()
            return output
        except Exception:
            return ""


class Scene(object):
    def __init__(self, path=None):
        self.path = path or SceneManager().current_scene_path

    # -----------------------------------------------------------

    @property
    def is_open(self):
        """
        Checks if this scene is currently open
        :return <bool:open> True if the scene is open - else False
        """
        return SceneManager().current_scene_path == self.path

    @property
    def name(self):
        return juniper.utilities.pathing.get_filename_only(self.path)

    # -----------------------------------------------------------

    def save(self):
        """
        Saves the current scene
        :return <bool:saved> True if the file was saved - else False
        """
        if(self.is_open):
            return self.__save()
        return False

    @juniper.engine.decorators.virtual_method
    def __save(self):
        raise NotImplementedError

    @save.override("painter")
    def __save(self):
        try:
            import substance_painter.project
            if(substance_painter.project.is_open() and substance_painter.project.needs_saving()):
                substance_painter.project.save()
            return True
        except Exception:
            return False

    # -----------------------------------------------------------

    @juniper.engine.decorators.virtual_method
    def save_as(self, file_path):
        """
        Saves the current file as the input file path
        :param <str:file_path> The path to save this file to
        """
        raise NotImplementedError

    # -----------------------------------------------------------

    @juniper.engine.decorators.virtual_method
    def open(self, force=True):
        """
        Opens this scene
        :param <bool:force> If True then the current scene is forceably closed
        :return <bool:success> True if the scene was opened - else False
        """
        raise NotImplementedError

    @open.override("designer")
    def open(self, force=True):
        import sd
        if(os.path.isfile(self.path)):
            try:
                package_manager = sd.getContext().getSDApplication().getPackageMgr()
                package_manager.loadUserPackage(self.path.replace("\\", "/"), True, True)
                return True
            except Exception:
                pass
        return False

    @open.override("painter")
    def open(self, force=True):
        import substance_painter.project
        if(substance_painter.project.is_open()):
            substance_painter.project.close()

        if(os.path.isfile(self.path)):
            substance_painter.project.open(self.path)
            return True
        return None

    # -----------------------------------------------------------

    def close(self, force=True):
        """
        Closes the scene (if it's currently open)
        :param [<bool:force>] If True then the scene is force closed
        """
        if(self.is_open):
            self.__close(force=force)

    @juniper.engine.decorators.virtual_method
    def __close(self, force=True):
        raise NotImplementedError

    @__close.override("painter")
    def __close(self, force=True):
        import substance_painter.project
        if(not force):
            self.save()
        substance_painter.project.close()

    # -----------------------------------------------------------

    @property
    def selection_sets(self):
        """
        Gets all selection sets in the current scene
        :return <[SelectionSet]:selection_sets> All selection sets in the current scene
        """
        return self.get_selection_sets()

    @juniper.engine.decorators.virtual_method
    def get_selection_sets(self):
        raise NotImplementedError

    @get_selection_sets.override("max")
    def get_selection_sets(self):
        import pymxs
        output = []
        for i in pymxs.runtime.selectionSets:
            output.append(juniper.dcc.types.scene.selection_set.SelectionSet(i.name))
        return output

    # -----------------------------------------------------------

    @property
    def nodes(self):
        """
        Gets all nodes in the current scene
        :return <[Node]:nodes> All nodes in the current scene
        """
        return self.get_nodes()

    def find_node(self, name, ignore_case=False):
        """
        Finds a node by its name
        :param <str:name> The name of the node to find
        :param [<bool:ignore_case>] Should case be ignored in the checks?
        :return <Node:node> The node if found - else None
        """
        for i in self.nodes:
            if(ignore_case and name.lower() == i.name.lower()):
                return i
            elif(name == i.name):
                return i
        return None

    @juniper.engine.decorators.virtual_method
    def get_nodes(self):
        raise NotImplementedError

    @get_nodes.override("max")
    def get_nodes(self):
        output = []
        import pymxs
        for i in pymxs.runtime.objects:
            output.append(juniper.dcc.types.scene.node.Node(i))
        return output

    @get_nodes.override("unreal")
    def get_nodes(self):
        import unreal
        output = []
        for i in unreal.EditorLevelLibrary.get_all_level_actors():
            output.append(juniper.dcc.types.scene.node.Node(i))
        return output

    # -----------------------------------------------------------

    @property
    def selection(self):
        return self.get_selection()

    @juniper.engine.decorators.virtual_method
    def get_selection(self):
        raise NotImplementedError

    @get_selection.override("max")
    def get_selection(self):
        output = []
        import pymxs
        for i in pymxs.runtime.selection:
            output.append(juniper.dcc.types.scene.node.Node(i))
        return output

    @get_selection.override("unreal")
    def get_selection(self):
        import unreal
        output = []
        for i in unreal.EditorLevelLibrary.get_selected_level_actors():
            node = juniper.dcc.types.scene.node.Node(i)
            output.append(node)
        return output

    @juniper.engine.decorators.virtual_method
    def clear_selection(self):
        """
        Clears the current node selection
        """
        raise NotImplementedError

    @clear_selection.override("max")
    def clear_selection(self):
        import pymxs
        pymxs.runtime.clearSelection()

    # -----------------------------------------------------------

    def explore(self):
        """
        Reveal the current scene file in windows explorer
        """
        subprocess.Popen(f'explorer /select,"{self.path}"')
