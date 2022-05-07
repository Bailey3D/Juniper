import os
import inspect
import traceback


def _decorator_print_traceback(func, *args, context="Log"):
    tb = traceback.extract_stack()[-3]
    print(f"InDev ({context.upper()}):")
    print(f"  File \"{tb[0]}\", line {tb[1]}, method {func.__name__}")
    for i in args:
        print(f"    \"{i}\"")


class todo(object):
    """Decorator which will log a todo warning for a method"""
    def __init__(self, *todo_str):
        self.todo_str = todo_str
    def __call__(self, func, *args, **kwargs):
        dec_self = self
        def wrapper(*args, **kwargs):
            _decorator_print_traceback(func, *self.todo_str, context="Todo")
            return func(*args, **kwargs)
        return wrapper
