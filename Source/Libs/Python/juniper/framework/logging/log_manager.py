import juniper.framework.types.singleton
import juniper.widgets as qt_utils
from juniper.framework.logging import q_log_entry, q_log_holder


class LogManager(object, metaclass=juniper.framework.types.singleton.Singleton):
    """Manager class used for various logging tasks"""
    def __init__(self):
        """"""
        self._q_log_holder = None
        self.main_window = qt_utils.get_dcc_main_window()

    @property
    def log_holder_widget(self):
        """Gets the current QLogHolder widget, creates it if it doesn't already exist
        :return <QLogHolder:log_holder> The log holder widget
        """
        if(not self._q_log_holder):
            self._q_log_holder = q_log_holder.QLogHolder()
            self._q_log_holder.show()
        return self._q_log_holder

    def add_log_entry(self, info_string, info_type, owning_module="Juniper", persistent=False):
        """Adds a new log entry
        :param <str:info_string> The info / description string for this log entry
        :param <str:info_type> The type of log this is, current options include ["Info", "Success", "Error", "Warning"]
        :param [<str:owning_module>] The name of the owning module (Ie, "Juniper"). Can be overriden for individual tools.
        :param [<bool:persistent>] Does this log persist until manually closed? Or is it swept up in the log holfer update loop?
        """
        log_entry = q_log_entry.QLogEntry(
            info_string,
            info_type,
            owning_module,
            persistent=persistent
        )
        self.log_holder_widget.addWidget(log_entry)
        self.log_holder_widget.refresh_position()
        return log_entry

    '''def __update_log_holder(self):
        """Updates the log holder widget to be in the bottom right of the main window"""
        dwmapi = ctypes.WinDLL("dwmapi")

        hwnd = qt_utils.get_dcc_hwnd()
        rect = RECT()
        DMWA_EXTENDED_FRAME_BOUNDS = 9
        dwmapi.DwmGetWindowAttribute(
            HWND(hwnd),
            DWORD(DMWA_EXTENDED_FRAME_BOUNDS),
            ctypes.byref(rect),
            ctypes.sizeof(rect)
        )
        bottom_right = [rect.right, rect.bottom]
        log_width_height = (self.log_holder_widget.sizeHint().width(), self.log_holder_widget.sizeHint().height())
        padding = 8

        self.log_holder_widget.setGeometry(
            bottom_right[0] - log_width_height[0] - padding,
            bottom_right[1] - log_width_height[1] - padding,
            log_width_height[0],
            log_width_height[1]
        ) '''
