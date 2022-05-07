import os
import sys
import inspect
import traceback as traceback_


class _Colours(object):
    RED   = "\033[1;31m"
    YELLOW = "\033[33m"
    BLUE  = "\033[1;34m"
    CYAN  = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD    = "\033[;1m"
    REVERSE = "\033[;7m"


class log_class(object):

    def __init__(self, context="InDev"):
        self.context = context

    def _ensure_context(self, context):
        if(context):
            return context
        else:
            return self.context

    def _log_traceback(self, log_text, context=None, logtype="Error", traceback=True, traceback_stack=None):
        context = self._ensure_context(context)
        if(not traceback_stack):
            traceback_stack = traceback_.extract_stack()[-3]
        if(traceback):
            print(f"{context} ({logtype.upper()}):  File \"{traceback_stack[0]}\", line {traceback_stack[1]}")
            print(f"  \"{log_text}\"")
        else:
            print(f"{context} ({logtype.upper()}):  {log_text}")

    def error(self, log_text, context=None, traceback=True, traceback_stack=None):
        sys.stdout.write(_Colours.RED)
        self._log_traceback(log_text, context=context, logtype="Error", traceback=traceback, traceback_stack=traceback_stack)
        sys.stdout.write(_Colours.RESET)

    def warning(self, log_text, context=None, traceback=True, traceback_stack=None):
        sys.stdout.write(_Colours.YELLOW)
        self._log_traceback(log_text, context=context, logtype="Warning", traceback=traceback, traceback_stack=traceback_stack)
        sys.stdout.write(_Colours.RESET)

    def info(self, log_text, context=None, traceback=False, traceback_stack=None):
        self._log_traceback(log_text, context=context, logtype="Info", traceback=traceback, traceback_stack=traceback_stack)


log = log_class()
