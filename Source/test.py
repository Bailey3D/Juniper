import juniper


class Plugin(object):
    def __init__(self):
        pass

    def __install__(self):
        """
        Runs the base install logic for this plugin
        """
        pass

    def __startup__(self):
        """
        Runs the base startup logic for this plugin
        """
        pass

    def __uninstall__(self):
        """
        Runs the base uninstall logic for this plugin
        """
        pass

    # ---------------------------------------------------

    @property
    def display_name(self):
        """
        :return <str:name> The display / friendly name for this plugin
        """
        pass

    @property
    def name(self):
        """
        :return <str:name> The code name for this plugin
        """
        pass

    @property
    def description(self):
        """
        :return <str:description> The description for this plugin
        """
        return ""

    @property
    def integration_method(self):
        """
        Integration type for the plugin, options include:
         - integrated, for plugins that are integrated directly into Juniper (menus, etc)
         - standalone, for plugins that should be treated as separate
         - separate, for plugins which are integrated to Juniper, but contain their own submens, etc
        :return <str:method> The integration method for this plugin
        """
        return "integrated"

    @property
    def internal(self):
        """
        :return <bool:internal> True if this is an internal (Juniper) plugin - else False
        """
        return True

    # ---------------------------------------------------

    @property
    def root(self):
        """
        :return <str:root> The root directory for this plugin
        """
        pass

    @property
    def enabled(self):
        """
        :return <bool:enabled> True if this plugin is enabled - else False
        """
        pass