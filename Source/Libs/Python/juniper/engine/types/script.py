import json
import os
import functools

import juniper.engine
import juniper.utilities.string


class Script(object):
    def __init__(self, script_path):
        """
        Barebones class for a script - used during the bootstrap phase
        This is overriden in `juniper.engine.types.script` for a version including more features
        """
        self.path = script_path.lower()

    def __eq__(self, other):
        if(type(other) == type(self)):
            return self.path == other.path
        return False

    def __hash__(self):
        return hash(self.path) + hash(Script)

    def __bool__(self):
        return len(self.metadata) > 0

    # ---------------------------------------------------------------------

    @property
    def file_name(self):
        """
        :return <str:name> The name of the file (minus file type)
        """
        return os.path.basename(self.path).split(".")[0]

    @property
    def file_type(self):
        """
        :return <str:type> The type of file this script is (Ie, .py)
        """
        return os.path.basename(self.path).split(".")[1]

    def run(self):
        """
        Runs this script in the current context
        """
        # TODO! Replace this with a per implementation override
        # we don't want maxscript poluting the base workspace!
        if(self.file_type == ".ms"):
            import pymxs
            with open(self.path, "r") as f:
                file_lines = f.read()
                pymxs.runtime.execute(file_lines)

        else:
            globals_ = globals()
            if(os.path.isfile(self.path)):
                import juniper_globals
                globals_["__file__"] = self.path
                globals_["__package__"] = os.path.dirname(self.path)
                globals_["__name__"] = "__main__"
                juniper_globals.set("__juniper_exec_file_path__", self.path)
                exec(open(self.path).read(), globals_)

    def sort_key(self):
        """
        :return <str:key> The key used to sort the script in a `sorted` call. Uses category + display name
        """
        return self.category + "|z_" + self.display_name  # "z_" used to prioritize subcategories at the top of menus

    # ---------------------------------------------------------------------

    @property
    def name(self):
        """
        :return <str:name> The code name for this script. For the friendly name use `self.display_name`
        """
        if("name" in self.metadata):
            return self.metadata["name"]
        if(self.file_name == "__init__"):
            return os.path.basename(os.path.dirname(self.path))
        return self.file_name

    @property
    def display_name(self):
        """
        :return <str:name> The display name for this script. Human readable.
        """
        if("display_name" in self.metadata):
            return self.metadata["display_name"]
        return juniper.utilities.string.snake_to_name(self.name)

    @property
    def summary(self):
        """
        :return <str:summary> The summary if specified - else ""
        """
        if("summary" in self.metadata):
            return self.metadata["summary"]
        return ""

    @property
    def category(self):
        """
        :return <str:category> The category for this script if specified
        """
        output = self.parent_category

        if("category" in self.metadata and not self.is_core):
            output += "|" + self.metadata["category"]

        return output

    @property
    def group(self):
        """
        Gets the group for this script. Group is a 1 deep categorization, unlike Cagegory, which can be N deep
        :return <str:group> The group for this script if specified - else ""
        """
        if("group" in self.metadata):
            return self.metadata["group"]
        return ""

    @property
    def description(self):
        """
        Gets the description for this script
        If unspecified - falls back to the summary
        :return <str:desc> The description - or "" if not specified
        """
        for i in ("desc", "description", "summary"):
            if(i in self.metadata):
                return self.metadata[i]
        return ""

    @property
    def type(self):
        """
        :return <str:type> The type of script this is (Ie, Tool, Script)
        """
        if("type" in self.metadata):
            return self.metadata["type"]
        return "script"

    @property
    def icon_path(self):
        """
        :return <str:path> The path to the icon if specified - else ""
        """
        if("icon" in self.metadata):

            module_root = self.path.lower().split("source")[0]

            possible_path = os.path.join(module_root, "resources", self.metadata["icon"])
            if(os.path.isfile(possible_path)):
                return possible_path

            possible_path = os.path.join(juniper.engine.JuniperEngine().workspace_root, "resources", self.metadata["icon"])
            if(os.path.isfile(possible_path)):
                return possible_path

        return ""

    # ---------------------------------------------------------------------

    @property
    def integration_type(self):
        """
        Gets how this script is integrated into Juiniper.
        Options are:
        - integrated, for scripts which should be integrated into the base Juniper implementation
        - standalone, for scripts which are added as a standalone module (Ie, separate menus)
        - separate, for scripts which are within the base Juniper implementation, but under their own subcategory
        :return <str:integration_type> The integration type - defaults to integrated if unspecified
        """
        if(self.path.lower().startswith(
            os.path.join(juniper.engine.JuniperEngine().workspace_root, "source")
        )):
            return "integrated"

        module_root = self.path.lower().split("source")[0]
        for i in os.listdir(module_root):
            if(i.endswith(".jplugin")):
                jplugin_path = os.path.join(module_root, i)
                with open(jplugin_path, "r") as f:
                    json_data = json.load(f)
                    if("integration_type" in json_data):
                        return json_data["integration_type"]

        return "integrated"

    @property
    def parent_category(self):
        """
        Gets the parent category for this script from its integration type
        (Ie, the name of the outermost menu)
        :return <str:category> The parent category - defaults to "Juniper"
        """
        output = "Juniper"

        integration_type = self.integration_type

        if(integration_type != "integrated"):
            # Get the parent module - as this will be either the separate submenu, or standalone menu name
            parent_module_name = None
            module_root = self.path.lower().split("source")[0]
            for i in os.listdir(module_root):
                if(i.endswith(".jplugin")):
                    parent_module_name = i.split(".")[0].capitalize()  # TODO! Friendly name
                    parent_module_name = juniper.utilities.string.snake_to_name(parent_module_name)
                    parent_module_name = parent_module_name.rstrip()
                    break

            if(integration_type == "separate"):
                # The "_" prefix is used to denote this is a separate section
                output += "|_" + parent_module_name
            elif(integration_type == "standalone"):
                output = parent_module_name

        return output

    @property
    def is_core(self):
        if("category" in self.metadata):
            return self.metadata["category"].lower() == "core"
        return False

    # ---------------------------------------------------------------------

    @property
    def __module_root(self):
        """
        Gets the root directory for this module by splitting at the "Source" directory
        (all scripts should be within the source directory - which is one deep from any root)
        :return <str:root> The root directory
        """
        return self.path.lower().split("source")

    @property
    @functools.lru_cache()
    def metadata(self):
        """
        Reads the Juniper file metadata for this script
        :return <dict:data> The file metadata
        """
        output = {}
        if(os.path.isfile(self.path)):
            with open(self.path, "r") as f:
                for line in f.readlines():
                    if(line.startswith(":")):
                        key = line.split(" ", 1)[0].lower().lstrip(":")
                        value = line.split(" ", 1)[1].rstrip("\n")
                        if(key in output):
                            output[key] += " " + value
                        else:
                            output[key] = value
        return output

    def get(self, key):
        """
        Gets a key from the file metadata of this script
        :param <str:key> The key to get
        :return <str:value> The value as stored in the script
        """
        key = key.lower()
        if(key in self.metadata):
            return self.metadata[key]
        return None

    # ---------------------------------------------------------------------

    @property
    def callbacks(self):
        """
        :return <[str]:callbacks> The names of all callbacks this script is bound to
        """
        callbacks = []
        if(self.get("callbacks")):
            for i in self.get("callbacks").lstrip("[").rstrip("]").split(","):
                callback_name = i.replace(" ", "").lower()
                callbacks.append(callback_name)
        return callbacks

    def is_bound_to_callback(self, callback_name):
        """
        Checks if a script is bound to a given callback
        :param <str:callback_name> The name of the callback to check
        :return <bool:state> True if this script is bound to the input callback - else False
        """
        return callback_name in self.callbacks

    # ---------------------------------------------------------------------

    def is_enabled_in_host(self, target_host):
        """
        Checks if this script is enabled in the current host
        This checks against the `supported_hosts` and `unsupported_hosts` metadata keys
        If neither are provided, we return True
        :param <str:target_host> The name of the host to check
        :return <bool:enabled> True if enabled - else False
        """
        target_host = target_host.lower()
        supported_hosts = []
        unsupported_hosts = []

        if(self.get("supported_hosts")):
            for i in self.get("supported_hosts").lstrip("[").rstrip("]").split(","):
                host_name = i.replace(" ", "").lower()
                supported_hosts.append(host_name)

        if(self.get("unsupported_hosts")):
            for i in self.get("unsupported_hosts").lstrip("[").rstrip("]").split(","):
                host_name = i.replace(" ", "").lower()
                unsupported_hosts.append(host_name)

        if(target_host not in unsupported_hosts):
            if(not supported_hosts or target_host in supported_hosts):
                return True

        return False
