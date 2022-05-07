class _DelegateManager(object):
    __instance__ = None
    def __init__(self):
        self._delegates = {}

    def broadcast(self, func, *args, **kwargs):
        """Broadcast a delegate by function reference
        :param <function:func> The function to delegate
        :param [<[],*args>] Optional arguments
        :param [<{},**kwargs>] Optional kwargs
        """
        if(func in self._delegates):
            self._delegates[func].broadcast(*args, **kwargs)

    def bind(self, parent, child):
        """Bind a function to a delegate function
        :param <function:parent> The parent function
        :paran <function:child> The child function
        """
        if(isinstance(parent.self, _DelegateDecoratorWrapper)):
            func = parent.self.func
            if(func in self._delegates):
                self._delegates[func]._add_child(child)

    def create(self, func):
        """Create a new delegate
        :param <function:func> The parent function
        """
        if(func not in self._delegates):
            d = self._Delegate(func)
            self._delegates[func] = d
        return self._delegates[func]

    class _Delegate(object):
        def __init__(self, func):
            self.func = func

            # methods which take no arguments
            self.child_methods = []

        def _add_child(self, child):
            """Add a child method to this delegate"""
            if(child not in self.child_methods):
                self.child_methods.append(child)

        def broadcast(self, *args, **kwargs):
            """Broadcast this delegates methods"""
            for i in self.child_methods:
                # TODO: Arguments
                i()


if(_DelegateManager.__instance__ is None):
    _DelegateManager.__instance__ = _DelegateManager()
DelegateManager = _DelegateManager.__instance__

# -------------------------------------------------------------------------

class _DelegateDecoratorWrapper(object):
    def __init__(self, func):
        self.func = func
        self.delegate = DelegateManager.create(func)

        def wrapper(*args, **kwargs):
            """Wrapper function returned for this delegate decorator"""
            output = self.func(*args, **kwargs)
            DelegateManager.broadcast(self.func, *args, **kwargs)
            return output

        self.wrapper = wrapper
        setattr(self.wrapper, "self", self)
        setattr(self.wrapper, "bind", self.bind)

    def bind(self, child):
        """Added as an attribute to the parent function to allow for adding children by:
        `parent_function.bind(child_function)`
        """
        DelegateManager.bind(self.wrapper, child)


def delegate(func):
    """Decorator used for setting a function as a delegate"""
    return _DelegateDecoratorWrapper(func).wrapper

# -------------------------------------------------------------------------

bind = DelegateManager.bind
