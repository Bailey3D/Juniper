"""
:type uninstall
:desc Uninstall the core juniper components
"""
import os


class Uninstall(object):
    def __init__(self):
        pass

    def remove_user_paths(self):
        """Remove the juniper data stored in appdata/roaming"""
        if(os.path.isfile(self.juniper_config_path)):
            os.remove(self.juniper_config_path)

    @property
    def juniper_config_path(self):
        """
        :return <str:path> The path to the juniper config.json as stored in appdata/roaming
        """
        return os.path.join(os.getenv("APPDATA"), "Juniper\\config.json")
