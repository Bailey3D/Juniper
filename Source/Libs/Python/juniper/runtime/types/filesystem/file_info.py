import os

import juniper.utilities.pathing
import juniper.utilities.filemgr


class FileInfo(object):
    def __init__(self, file_path, frozen=False):
        """
        Class used to access metadata on a file in certain ways
        :param <str:file_path> The path to the file
        :param [<bool:frozen>] If True then the data stored in this class will not update with the file unless the `update` method is called
        """
        self.file_path = file_path
        self.frozen = frozen

        self.__checksum = None
        self.__exists = None
        self.__last_edit_time = None
        self.__size = None
        self.__name = None
        self.__extension = None

        self.update()

    def update(self):
        """
        Updates the file information
        """
        if(self.outdated):
            self.__exists = self.currently_exists
            self.__name = juniper.utilities.pathing.get_filename_only(self.file_path)
            self.__extension = os.path.splitext(self.file_path)[1]

            # initialize properties that rely on the file existing
            if(self.__exists):
                self.__checksum = self.current_checksum
                self.__last_edit_time = self.current_last_edit_time
                self.__size = self.current_size

    @property
    def outdated(self):
        """
        :return <bool:outdated> True if this file info instance is not up to date with that on disk
        """
        return self.__last_edit_time != self.current_last_edit_time

    # ---------------------------------------------------------------------------

    @property
    def name(self):
        """
        :return <str:name> The name of the file (minus any extensions)
        """
        if(not self.frozen):
            self.update()
        return self.__name

    @property
    def extension(self):
        """
        :return <str:ext> The extension of the file - I.e. "json", "png", etc.
        """
        if(not self.frozen):
            self.update()
        return self.__extension

    # ---------------------------------------------------------------------------

    @property
    def checksum(self):
        """
        :return <str:checksum> Checksum of the file
        """
        if(not self.frozen):
            self.update()
        return self.__checksum()

    @property
    def current_checksum(self):
        """
        :return <str:checksum> The checksum of the file as it currently exists on disk
        """
        return juniper.utilities.filemgr.checksum(self.file_path)

    # ---------------------------------------------------------------------------

    @property
    def exists(self):
        """
        :return <bool:exists> True if the file exists - else False
        """
        if(not self.frozen):
            self.update()
        return self.__exists()

    @property
    def currently_exists(self):
        """
        :return <bool:exists> True if the file currently exists on disk - else False
        """
        return os.path.isfile(self.file_path)

    # ---------------------------------------------------------------------------

    @property
    def last_edit_time(self):
        """
        :return <int:time> The most recent edit time for the file
        """
        if(not self.frozen):
            self.update()
        return self.__last_edit_time

    @property
    def current_last_edit_time(self):
        """
        :return <int:time> The last edit time of the file on disk
        """
        return os.path.getmtime(self.file_path)

    # ---------------------------------------------------------------------------

    @property
    def size(self):
        """
        :return <int:size> The size of the file in bytes
        """
        if(not self.frozen):
            self.update()
        return self.__size

    @property
    def current_size(self):
        """
        :return <int:size> The size of the file on disk in bytes
        """
        return os.path.getsize(self.file_path)
