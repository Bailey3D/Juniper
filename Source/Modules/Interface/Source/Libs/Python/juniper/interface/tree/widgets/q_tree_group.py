from juniper.runtime.widgets import q_collapsible_widget


class QHubGroup(q_collapsible_widget.QCollapsibleWidget):
    def __init__(self, title, parent=None, tint=None, tab_content=True):
        super(QHubGroup, self).__init__(
            parent=parent,
            title=title,
            collapsed=True,
            tint=tint,
            show_border=True,
            tab_content=tab_content,
            tab_multiplier=1.0
        )

        self.__child_groups = {}

    def add_group(self, group_name):
        """Adds a child group to this hub group
        :param <str:group_name> The name of the group to add
        :return <QCollapsibleWidget:group> The group widget that was created/cached
        """
        if(group_name not in self.__child_groups):
            self.__child_groups[group_name] = q_collapsible_widget.QCollapsibleWidget(
                parent=self,
                title=group_name,
                show_border=False,
                tab_content=True,
                tab_multiplier=2.0
            )
            self.addWidget(self.__child_groups[group_name])
        return self.__child_groups[group_name]

    def add_titlebar_widget(self, widget):
        """Adds a widget to the title bar
        :param <QWidget:widget> The widget to add
        """
        self.addWidget(widget, to_title=True)
