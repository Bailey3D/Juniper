import datetime
import os
from qtpy import QtWidgets, QtCore, QtGui, uic

import juniper.paths
import juniper.utilities.string as string_utils


class QLogEntry(QtWidgets.QWidget):
    def __init__(self, info_string, info_type, owning_plugin, persistent=False):
        """
        A single log entry widget - added as a child to the log holder
        :param <str:info_string> The info / description string for this log entry
        :param <str:info_type> The type of log this is, current options include ["Info", "Success", "Error", "Warning"]. Icons are retrieved from this name.
        :param <str:owning_plugin> The name of the owning plugin (Ie, "Juniper"). Can be overriden for individual tools.
        :param [<bool:persistent>] Does this log persist until manually closed? Or is it swept up in the log holfer update loop?
        """
        super(QLogEntry, self).__init__()
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setFixedHeight(90)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

        #
        self.persistent = persistent
        self.creation_time = datetime.datetime.now()

        # layout
        self._layout = QtWidgets.QHBoxLayout()
        self._layout.addStretch()
        self.setLayout(self._layout)

        # frame
        self._frame = QtWidgets.QFrame()
        self._frame.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)
        self._layout.addWidget(self._frame)

        # styling / properties
        self.setStyleSheet("""
            QWidget{
                background-color:rgba(50, 50, 50, 255);
            }
        """)

        # uic
        self.uic_path = __file__.replace(".py", ".ui")
        uic.loadUi(self.uic_path, baseinstance=self._frame)
        self.ui = self._frame

        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_close.setFixedSize(30, 30)

        self.ui.lbl_title.setText(f"""<p><span style="font-size:14px"><strong>{info_type}</strong></span></p>""")

        info_string = string_utils.truncate(info_string, 125, do_ellipsis=True)
        self.ui.lbl_description.setText(f"""<span style="font-size:13px">{info_string}</span>""")
        self.ui.lbl_description.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.ui.lbl_owner.setText(f"""<span style="font-size:11px; font-weight: lighter;">{owning_plugin}</span>""")

        btn_icon_size = 32
        icon = QtGui.QIcon(os.path.join(juniper.paths.root(), f"Resources\\Icons\\Standard\\{info_type}.png"))
        self.ui.btn_icon.setFixedSize(btn_icon_size, btn_icon_size)
        self.ui.btn_icon.setIcon(icon)
        self.ui.btn_icon.setIconSize(QtCore.QSize(btn_icon_size, btn_icon_size))

    def close(self):
        """Closes this log widget"""
        self.setParent(None)
        self.deleteLater()
