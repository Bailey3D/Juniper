from qtpy import QtWidgets, QtCore


class QVScrollLayout(QtWidgets.QVBoxLayout):
    """A scrollable version of QVBoxLayout"""
    def __init__(self, show_scroll_handles=True):
        super(QVScrollLayout, self).__init__()
        self.show_scroll_handles = show_scroll_handles

        self.setMargin(0)
        self.setSpacing(0)

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setMargin(0)
        self.main_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_layout)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidget(self.main_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBar(None)

        if(not self.show_scroll_handles):
            self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.addWidget(self.scroll_area, outer_layout=True)

    def addWidget(self, wgt, outer_layout=False):
        if(outer_layout):
            super(QVScrollLayout, self).addWidget(wgt)
        else:
            self.main_layout.addWidget(wgt)

    def addLayout(self, layout, outer_layout=False):
        if(outer_layout):
            super(QVScrollLayout, self).addLayout(layout)
        else:
            self.main_layout.addLayout(layout)

    def addStretch(self, outer_layout=False):
        if(outer_layout):
            super(QVScrollLayout, self).addStretch()
        else:
            self.main_layout.addStretch()
