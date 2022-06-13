import functools
import os


class FileMetadata(object):
    def __init__(self, file_path):
        self.file_path = file_path

    @functools.lru_cache(maxsize=8)
    def get(self, key):
        if(os.path.isfile(self.file_path)):
            key = f":{key.lower()} "

            with open(self.file_path, "r") as f:
                for line in f.readlines():
                    if(line.startswith(key)):
                        return line.split(" ", 1)[1].rstrip("\n")
        return None
