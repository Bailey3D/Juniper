"""
Time based functionality
"""
import time


class Timer(object):
    def __init__(self):
        """
        Class used inside a `with` statement to measure timings

        ```
        with Timer() as t:
            print(t.duration)
        ```
        """
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback): 
        pass

    @property
    def duration(self):
        """
        :return <float:seconds> The elapsed duration in seconds
        """
        return time.time() - self.start_time
