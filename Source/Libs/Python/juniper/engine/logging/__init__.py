import juniper.runtime.types.misc.log
import juniper.engine.logging.log_manager


class _LogEntry(object):
    """
    A log entry object - contains all data on a single log entry
    """
    def __init__(
        self,
        log_text="",
        log_type="Info",
        silent=True,
        context=None,
        traceback=False,
        traceback_stack=None,
        persistent=False,
        log_func=juniper.runtime.types.misc.log.log.info
    ):
        self.log_text = log_text
        self.log_type = log_type
        self.silent = silent
        self.context = context
        self.traceback = traceback
        self.traceback_stack = traceback_stack
        self.persistent = persistent
        self.log_func = log_func


class Log(object):
    def __init__(self, plugin="Juniper"):
        self.juniper_log = juniper.runtime.types.misc.log.log_class(context=plugin)
        self.plugin = plugin

        self._held_entries = []
        self._holding = False

    # -------------------------------------------------------------------------

    @property
    def holding(self):
        """
        :return <bool:holding> True if we're currently holding log outputs - else False
        """
        return self._holding

    def hold(self):
        """
        Begin holding log entries - supresses outupt until released
        """
        if(not self.holding):
            self._holding = True

    # -------------------------------------------------------------------------

    def __get_num_held_entries_of_type(self, type_):
        """
        Gets the number of held log entries of a given type
        :param <str:type_> The type of entries to get the count for
        :return <int:count> Number of held entries of the input type
        """
        count = 0
        for i in self._held_entries:
            if(i.log_type == type_):
                count += 1
        return count

    @property
    def num_held_errors(self):
        """
        Gets the number of held errors
        :return <int:count> Number of held errors
        """
        return self.__get_num_held_entries_of_type("Error")

    @property
    def num_held_warnings(self):
        """
        Gets the number of held errors
        :return <int:count> Number of held warnings
        """
        return self.__get_num_held_entries_of_type("Warning")

    @property
    def num_held_infos(self):
        """
        Gets the number of held errors
        :return <int:count> Number of held infos
        """
        return self.__get_num_held_entries_of_type("Info")

    @property
    def num_held_successes(self):
        """
        Gets the number of held errors
        :return <int:count> Number of held successes
        """
        return self.__get_num_held_entries_of_type("Success")

    # -------------------------------------------------------------------------

    def release(self, success_text="", warning_text="", error_text="", info_text="", force_silent=True):
        """
        Releases log holding and outputs all held outputs
        :param [<str:release_text>] Optional release text for the batch output
        :param [<bool:force_silent>] If True then all popups will be suppressed - except for the release popup
        :return <bool:success> True if logs were successfully released - else False
        """
        log_counts = {
            "Error": 0,
            "Warning": 0,
            "Info": 0,
            "Success": 0
        }

        if(self.holding):
            self._holding = False
            for i in self._held_entries:
                silent = force_silent or i.silent
                self.__do_log(
                    i.log_text,
                    i.log_type,
                    silent=silent,
                    context=i.context,
                    traceback=i.traceback,
                    traceback_stack=i.traceback_stack,
                    persistent=i.persistent,
                    log_func=i.log_func
                )
                log_counts[i.log_type] += 1

            if(log_counts["Error"] > 0):
                output_text = error_text or (f"""{log_counts["Error"]} Errors reported""")
                self.error(output_text, silent=False, traceback=False)
            elif(log_counts["Warning"] > 0):
                output_text = warning_text or (f"""{log_counts["Warning"]} Warnings reported""")
                self.warning(output_text, silent=False, traceback=False)
            elif(log_counts["Info"] > 0):
                output_text = info_text or (f"""{log_counts["Info"]} sets of information to report.""")
                self.info(output_text, silent=False)
            elif(log_counts["Success"] > 0):
                output_text = success_text or (f"""{log_counts["Success"]} actions complete successfully.""")
                self.success(output_text, silent=False)

            self._held_entries = []

            return True
        else:
            return True

    # -------------------------------------------------------------------------

    def __do_log(
        self,
        log_text,
        log_type,
        silent=False,
        context=None,
        traceback=True,
        traceback_stack=None,
        log_func=None,
        persistent=False
    ):
        if(not self.holding):
            log_func(log_text, context=context, traceback=traceback, traceback_stack=traceback_stack)
            if(not silent):
                juniper.engine.logging.log_manager.LogManager().add_log_entry(
                    log_text,
                    log_type,
                    context or self.plugin,
                    persistent=persistent
                )
        else:
            log_entry = _LogEntry(
                log_text=log_text,
                log_type=log_type,
                silent=silent,
                context=context,
                traceback=traceback,
                traceback_stack=traceback_stack,
                persistent=persistent,
                log_func=log_func
            )
            self._held_entries.append(log_entry)

    def error(self, log_text, silent=False, context=None, traceback=True, traceback_stack=None, persistent=False):
        self.__do_log(
            log_text, "Error",
            silent=silent,
            context=context,
            traceback=traceback,
            traceback_stack=traceback_stack,
            log_func=self.juniper_log.error,
            persistent=persistent
        )

    def warning(self, log_text, silent=False, context=None, traceback=True, traceback_stack=None, persistent=False):
        self.__do_log(
            log_text,
            "Warning",
            silent=silent,
            context=context,
            traceback=traceback,
            traceback_stack=traceback_stack,
            log_func=self.juniper_log.warning,
            persistent=persistent
        )

    def info(self, log_text, silent=False, context=None, persistent=False):
        self.__do_log(
            log_text,
            "Info",
            silent=silent,
            context=context,
            traceback=False,
            traceback_stack=None,
            log_func=self.juniper_log.info,
            persistent=persistent
        )

    def success(self, log_text, silent=False, context=None, persistent=False):
        self.__do_log(
            log_text,
            "Success",
            silent=silent,
            context=context,
            traceback=False,
            traceback_stack=None,
            log_func=self.juniper_log.info,
            persistent=persistent
        )
