import functools
import glob
import json
import os

import juniper.engine.types.script


class Plugin(object):
    def __init__(self, jplugin_path):
        """
        Barebones class for a plugin - used during the bootstrap phase
        This is overriden in `juniper.engine.types.plugin` for a version including more features
        """
        self.jplugin_path = jplugin_path

    def __bool__(self):
        # TODO! Add in checks for whether plugin is enabled in the current context
        return True

    @property
    @functools.lru_cache()
    def metadata(self):
        """
        :return <dict:data> The jplugin file data loaded as a json dict
        """
        with open(self.jplugin_path, "r") as f:
            return json.load(f)

    @property
    @functools.lru_cache()
    def name(self):
        """
        :return <str:name> The code name of this plugin
        """
        return os.path.basename(self.jplugin_path).split(".")[0]

    @property
    def root(self):
        return os.path.dirname(self.jplugin_path)

    @property
    def scripts(self):
        output = []
        for i in glob.iglob(self.root + "\\Source\\Scripts\\**\\*.*", recursive=True):
            script = juniper.engine.types.script.Script(i)
            if(script and script.get("type") == "script"):
                output.append(script)
        return output

    @property
    def tools(self):
        output = []
        for i in glob.iglob(self.root + "\\Source\\Tools\\**\\*.*", recursive=True):
            script = juniper.engine.types.script.Script(i)
            if(script and script.get("type") == "tool"):
                output.append(script)
        return output

    @property
    def is_host_plugin(self):
        return "\\juniperhosts\\" in self.jplugin_path.lower()

