import ctypes
from ctypes.wintypes import HWND, DWORD, RECT
import datetime
from qtpy import QtWidgets, QtCore

import juniper.widgets as qt_utils


class QLogHolder(QtWidgets.QWidget):
    def __init__(self):
        """
        Container class / widget used for displaying / holding log entries
        """
        super(QLogHolder, self).__init__(parent=qt_utils.get_main_window())

        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        qt_utils.initialize_host_window_parenting(self)

        self.children = []

        #
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setAlignment(QtCore.Qt.AlignBottom)
        self.setLayout(self._layout)

        # display timers
        self.timer_check_interval_seconds = 2
        self.max_log_display_time_seconds = 10
        self.check_timer = QtCore.QTimer()
        self.check_timer.timeout.connect(self.refresh)
        self.check_timer.start(self.timer_check_interval_seconds * 1000)

        # drag timer
        # Note: This updates 20 times a second, it's not too expensive of a function
        # but if we have issues here may be the first place to look
        self.__have_cached_parent_hwnd_data = False
        self.timer_update_geometry_interval_seconds = 0.05
        self.timer_update_geometry = QtCore.QTimer()
        self.timer_update_geometry.timeout.connect(self.refresh_position)
        self.timer_update_geometry.start(self.timer_update_geometry_interval_seconds * 1000)

    def addWidget(self, widget):
        """
        Adds a widget to the holder - this should only be log entries!
        :param <QLogEntry:widget> The widget to add
        """
        self._layout.addWidget(widget)
        if(widget not in self.children):
            self.children.append(widget)
        self.refresh()

    def sizeHint(self):
        """
        Overrides sizeHint to take into account the contents
        :return <QSize:size> The size hint
        """
        width = 0
        height = 0

        for i in reversed(self.children):
            try:
                width = max(i.sizeHint().width(), width)
                height += i.sizeHint().height() + self._layout.spacing()
            except Exception:
                self.children.remove(i)

        return QtCore.QSize(width, height)

    def refresh(self):
        """
        Updates the log holder and contents
        """
        # check for outdated widgets
        current_time = datetime.datetime.now()
        num_deleted = 0
        for i in self.children:
            if(not i.persistent):
                if((current_time - i.creation_time).total_seconds() > self.max_log_display_time_seconds):
                    num_deleted += 1
                    try:
                        i.close()
                    except Exception:  # for the "Internal C++ Object already deleted" exception, which is handled after this loop
                        pass
                    else:  # if we remove 1 then wait until next loop, to ensure we aren't closing everything in one big batch
                        break

        # remove invalid entries
        for i in reversed(self.children):
            if(not i):
                self.children.pop(i)

        # update position with window
        self.refresh_position(force=True)

    def refresh_position(self, force=False):
        """
        Updates the log holder widget to be in the bottom right of the main window
        """
        if(not self.__have_cached_parent_hwnd_data):
            self.__dwmapi = ctypes.WinDLL("dwmapi")
            self.__parent_hwnd = qt_utils.get_host_hwnd()
            self.__hwnd_cache = HWND(self.__parent_hwnd)
            self.__have_cached_parent_hwnd_data = True
            self.__dword_frame_bounds = DWORD(9)  # DMWA_EXTENDED_FRAME_BOUNDS
            self.__prev_rect_bottom_right = None

        rect = RECT()
        self.__dwmapi.DwmGetWindowAttribute(
            self.__hwnd_cache,
            self.__dword_frame_bounds,
            ctypes.byref(rect),
            ctypes.sizeof(rect)
        )
        bottom_right = (rect.right, rect.bottom)

        if(not force and self.__prev_rect_bottom_right == (rect.right, rect.bottom)):
            return

        log_width_height = (self.sizeHint().width(), self.sizeHint().height())

        padding = 8
        self.setGeometry(
            bottom_right[0] - log_width_height[0] - padding,
            bottom_right[1] - log_width_height[1] - padding,
            log_width_height[0],
            log_width_height[1]
        )
        self.__prev_rect_bottom_right = bottom_right
