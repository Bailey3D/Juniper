import time
import queue
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class _FileWatcher(PatternMatchingEventHandler):
    def __init__(self, queue_, patterns, parent=None):
        """
        Generic class used to watch a file / directory - only used internally by the `FileWatcher` class
        """
        super(_FileWatcher, self).__init__(patterns=patterns)
        self.__queue = queue_
        self.__parent = parent

    def process(self, event):
        self.__queue.put(event)

    def on_moved(self, event):
        if(self.__parent and self.__parent.on_moved):
            self.__parent.on_moved(event)

    def on_created(self, event):
        if(self.__parent and self.__parent.on_created):
            self.__parent.on_created(event)

    def on_deleted(self, event):
        if(self.__parent and self.__parent.on_deleted):
            self.__parent.on_deleted(event)

    def on_modified(self, event):
        if(self.__parent and self.__parent.on_modified):
            self.__parent.on_modified(event)

    def on_any_event(self, event):
        if(self.__parent and self.__parent.on_any_event):
            self.__parent.on_any_event(event)


class FileWatcher(object):
    def __init__(self, path, pattern="*"):
        """
        Generic file watcher class
        :param <str:path> The path to the file / directory to watch
        """
        self.__pattern = [pattern]
        self.__path = path

        self.__queue = queue.Queue()
        self.__worker = threading.Thread(target=FileWatcher.__process_queue, args=(self.__queue,))
        self.__worker.setDaemon(True)
        self.__worker.start()

        self.__event_handler = _FileWatcher(self.__queue, patterns=self.__pattern, parent=self)
        self.__observer = Observer()
        self.__observer.schedule(self.__event_handler, path=self.__path, recursive=True)
        self.__observer.start()

        self._bound_calls = {
            self.on_modified: [],
            self.on_created: [],
            self.on_deleted: [],
            self.on_any_event: [],
            self.on_moved: []
        }

    # ----------------------------------------------------------------------------

    def bind(self, parent, child):
        """
        Binds a method to call whenever an update happens
        """
        if(parent in self._bound_calls):
            if(child not in self._bound_calls[parent]):
                self._bound_calls[parent].append(child)

    def _process_bindings(self, parent, event):
        if(parent in self._bound_calls):
            for i in self._bound_calls[parent]:
                i(event)

    # ----------------------------------------------------------------------------

    def on_modified(self, event):
        """
        Called whenever a file is modified
        """
        self._process_bindings(self.on_modified, event)

    def on_created(self, event):
        """
        Called whenever a file is created
        """
        self._process_bindings(self.on_created, event)

    def on_deleted(self, event):
        """
        Called whenever a file is deleted
        """
        self._process_bindings(self.on_deleted, event)

    def on_any_event(self, event):
        """
        Called whenever any event is fired
        """
        self._process_bindings(self.on_any_event, event)

    def on_moved(self, event):
        """
        Called whenever a file is moved
        """
        self._process_bindings(self.on_moved, event)

    # ----------------------------------------------------------------------------

    @staticmethod
    def __process_queue(queue_):
        while True:
            if(not queue_.empty()):
                event = queue_.get()
            else:
                time.sleep(1)
