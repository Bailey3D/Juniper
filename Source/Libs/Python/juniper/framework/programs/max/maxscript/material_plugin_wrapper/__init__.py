# TODO~ Proper wrapping of MXS plugins in Python
import textwrap


class RolloutWrapper(object):
    def __init__(self):
        pass


class MaterialPluginWrapper(object):
    def __init__(self):
        pass

    # -------------------------------------------------------------

    # -------------------------------------------------------------

    @property
    def name(self):
        return "JuniperMaterial"

    @property
    def class_id_lower(self):
        # TODO~
        return "123456"

    @property
    def class_id_upper(self):
        # TODO~
        return "789012"

    @property
    def plugin_class(self):
        return "material"

    @property
    def display_name(self):
        return "Juniper Material Plugin"

    @property
    def extends(self):
        return "Standard"
        #import pymxs
        #return pymxs.runtime.Standard

    @property
    def replace_ui(self):
        return True

    @property
    def category(self):
        return "Juniper"

    # -------------------------------------------------------------

    def __mxs_header(self):
        output = textwrap.dedent(f"""
            plugin material {self.name}
            name:"{self.display_name}"
            classID:#({self.class_id_lower}, {self.class_id_upper})
            extends:{str(self.extends)}
            replaceUI:{self.replace_ui}
            version:1
            category:{self.category}
        """)
        return output

    def __mxs_repr__(self):
        output = ""
        output += self.__mxs_header()
        output += "("
        output += ")"
        return output


a = MaterialPluginWrapper()
print(a.__mxs_repr__())