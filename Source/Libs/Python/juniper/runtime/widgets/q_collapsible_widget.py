from qtpy import QtWidgets, QtCore, QtGui


DEFAULT_HEIGHT = 24  # height of the area


class _QArrow(QtWidgets.QFrame):
    def __init__(self, parent=None, collapsed=False, height=DEFAULT_HEIGHT):
        super(_QArrow, self).__init__(parent=parent)
        self.setMaximumSize(height, height)

        self._collapsed = collapsed

        self._arrow_horizontal = (QtCore.QPointF(7.0, 8.0), QtCore.QPointF(17.0, 8.0), QtCore.QPointF(12.0, 13.0))
        self._arrow_vertical = (QtCore.QPointF(8.0, 7.0), QtCore.QPointF(13.0, 12.0), QtCore.QPointF(8.0, 17.0))

        self._arrow = None
        self._set_arrow(int(self._collapsed))

    def _set_arrow(self, collapsed):
        if(collapsed):
            self._arrow = self._arrow_vertical
        else:
            self._arrow = self._arrow_horizontal

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtGui.QColor(192, 192, 192))
        painter.setPen(QtGui.QColor(64, 64, 64))
        painter.drawPolygon(self._arrow)
        painter.end()


class _QTitleFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, title="", collapsed=False, tint=None, border=True, height=DEFAULT_HEIGHT):
        super(_QTitleFrame, self).__init__(parent=parent)
        self.height = height
        self.setMinimumHeight(height)
        self.move(QtCore.QPoint(height, 0))

        _style_sheet = f"border:{1 if border else 0}px solid rgba(0, 0, 0, 100);"

        if(tint):
            _style_sheet += "background: " + tint.css + ";"

        self.setStyleSheet(_style_sheet)

        self._q_layout = QtWidgets.QHBoxLayout(self)
        self._q_layout.setContentsMargins(0, 0, 0, 0)
        self._q_layout.setSpacing(0)

        self._title = title
        self._collapsed = collapsed

        self._initialize_arrow()
        self._initialize_title()
        self._initialize_title_layout()

    def _set_title(self, title):
        self._title = title
        self._q_title.setText(self._title)

    def _initialize_arrow(self):
        self._q_arrow = _QArrow(collapsed=self._collapsed, parent=self, height=self.height)
        self._q_arrow.setStyleSheet("border:0px")
        self._q_layout.addWidget(self._q_arrow)
        return self._q_arrow

    def _initialize_title(self):
        self._q_title = QtWidgets.QLabel(self._title)
        self._q_title.setMinimumHeight(self.height)
        self._q_title.move(QtCore.QPoint(self.height, 0))
        self._q_title.setStyleSheet("border:0px")
        self._q_layout.addWidget(self._q_title)
        return self._q_title

    def _initialize_title_layout(self):
        # layout for additional buttons in the title frame..
        self._q_additional_buttons_widget = QtWidgets.QWidget()
        self._q_additional_buttons_widget.setContentsMargins(0, 0, 0, 0)
        self._q_additional_buttons_layout = QtWidgets.QHBoxLayout()
        self._q_additional_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._q_additional_buttons_layout.setSpacing(0)
        self._q_additional_buttons_layout.setMargin(0)
        self._q_additional_buttons_widget.setLayout(self._q_additional_buttons_layout)
        self._q_additional_buttons_widget.setStyleSheet("border:0px;")

        self._q_layout.addWidget(self._q_additional_buttons_widget)
        self._q_additional_buttons_layout.setAlignment(QtCore.Qt.AlignRight)

    def mousePressEvent(self, event):
        self.emit(QtCore.SIGNAL("clicked()"))
        return super(_QTitleFrame, self).mousePressEvent(event)


class QCollapsibleWidget(QtWidgets.QWidget):
    def __init__(
        self, parent=None, title=None, collapsed=True, tint=None, show_border=True,
        height=DEFAULT_HEIGHT, tab_content=False, tab_multiplier=1.0
    ):
        """
        A collapsible QWidget
        :param [<QWidget:parent>] The parent widget
        :param [<str:title>] The title for this widget
        :param [<bool:collapsed>] If True then the widget will be collapsed
        :param [<bool:show_border>] If True then the widget border will be shown
        :param [<int:height>] The height of the clickable section
        :param [<bool:tab_content>] Should child widgets be indented?
        :param [<float:tab_multiplier>] Multiplier applied to the tab width
        """
        super(QCollapsibleWidget, self).__init__()
        parent.addWidget(self)

        self.tint = tint
        self.__num_children = 0

        self._collapsed = collapsed
        self._q_title_frame = None
        self._q_content_layout = None
        self._q_content = None

        self._q_main_layout = QtWidgets.QVBoxLayout(self)
        self._q_main_layout.setAlignment(QtCore.Qt.AlignTop)

        # init title frame
        self._q_title_frame = _QTitleFrame(title=title, collapsed=self._collapsed, tint=self.tint, border=show_border, height=height)
        self._q_main_layout.setContentsMargins(0, 0, 0, 0)
        self._q_main_layout.setSpacing(0)
        self._q_main_layout.addWidget(self._q_title_frame)

        # init contents
        self._q_content = QtWidgets.QWidget()
        self._q_content_layout = QtWidgets.QVBoxLayout()
        self._q_content_layout.setContentsMargins(height * 0.5 * tab_multiplier if tab_content else 0, 0, 0, 0)
        self._q_content_layout.setSpacing(0)
        self._q_content_layout.setAlignment(QtCore.Qt.AlignTop)
        self._q_content.setLayout(self._q_content_layout)
        self._q_content.setVisible(not self._collapsed)
        self._q_main_layout.addWidget(self._q_content)

        # background tinting
        if(tint):
            palette = self._q_content.palette()
            palette.setColor(QtGui.QPalette.Base, tint.qcolor)
            self._q_content.setPalette(palette)

        # init collapsible
        QtCore.QObject.connect(self._q_title_frame, QtCore.SIGNAL("clicked()"), self.toggleCollapsed)

    def set_title(self, title):
        """
        Sets the title
        :param <str:title> The title for the widget
        """
        self._title = title
        self._q_title_frame._set_title(title)

    def addLayout(self, layout):
        """
        Adds a child layout to this widget
        :param <QLayout:layout> The layout to add
        """
        self._q_content_layout.addLayout(layout)

    def addWidget(self, widget, to_title=False):
        """Adds a widget to the collapsible layout
        :param <QWidget:widget> The widget to add
        :param [<bool:to_title>] If True then the widget is added to the titlebar instead
        """
        if(to_title):
            self._q_title_frame._q_additional_buttons_layout.addWidget(widget)
        else:
            self.__num_children += 1
            self._q_content_layout.addWidget(widget)

    def expand(self):
        """
        Expands this widget
        """
        self._set_collapsed(False)

    def collapse(self):
        """
        Collapses this widget
        """
        self._set_collapsed(True)

    @property
    def collapsed(self):
        """
        :return <bool:collapsed> Returns True if this widget is currently collapsed - else False
        """
        return self._collapsed

    def _set_collapsed(self, collapsed):
        self._q_content.setVisible(not collapsed)
        self._collapsed = collapsed
        self._q_title_frame._q_arrow._set_arrow(int(self._collapsed))

    def toggleCollapsed(self):
        self._set_collapsed(not self._collapsed)

    @property
    def num_children(self):
        """
        :return <int:num_children> The number of child widgets added to this widget
        """
        return self.__num_children
