"""
Abstract class for an asset exporter
"""
import abc


class AssetExporterTemplate(object, metaclass=abc.ABCMeta):
    def __init__(self, target_asset):
        """
        Abstracted base class for asset exporters
        :param <object:target_asset> The target asset to export
        """
        self.__target_asset = target_asset

        self.failure_step = None  # name of the method where execution fails

        self.exported_file_paths = []
        self.__export_dir_override = None
        self.__asset_name_override = None

    # -------------------------------------------------------------

    @property
    def target_asset(self):
        """
        :return <object:asset> The target asset to export
        """
        return self.__target_asset

    @target_asset.setter
    def target_asset(self, value):
        """
        Sets the target asset to export. Also wipes all data specific to the previous asset.
        :param <object:value> The asset to export
        """
        if(self.__target_asset != value):
            self.__target_asset = value
            self.exported_file_paths = []

    # -------------------------------------------------------------

    @property
    def asset_name(self):
        """
        :return <str:asset_name> The name of the asset file
        """
        if(self.__asset_name_override is not None):
            return self.__asset_name_override
        return self.get_asset_name()

    @asset_name.setter
    def asset_name(self, value):
        """
        :param <str:value> Override for the asset name
        """
        self.__asset_name_override = value

    @abc.abstractmethod
    def get_asset_name(self):
        """
        Gets the name to export this asset under
        :return <str:name> The name of the asset
        """
        raise NotImplementedError

    # -------------------------------------------------------------

    @property
    def export_dir(self):
        """
        :return <str:export_dir> The directory to export this asset to
        """
        if(self.__export_dir_override is not None):
            return self.__export_dir_override
        return self.get_export_dir()

    @export_dir.setter
    def export_dir(self, path):
        """
        :param <str:export_dir> Override for the directory to export this asset to
        """
        self.__export_dir_override = path

    @abc.abstractmethod
    def get_export_dir(self):
        """
        Gets the directory to export this asset to given the current settings
        :return <str:dir> The directory to export to
        """
        raise NotImplementedError

    # -------------------------------------------------------------

    @abc.abstractmethod
    def validate(self):
        """
        Validates whether the exporter can run with the current settings
        :return <bool:valid> True if the exporter can be ran - else False
        """
        pass

    # -------------------------------------------------------------

    def execute(self):
        """
        Runs the exporter
        :return <bool:success> True if the export ran successfully - else False
        """
        success = self.validate()
        if(not success):
            self.failure_step = "validation"

        if(success):
            success = self.pre_export() is not False
            if(not success):
                self.failure_step = "pre_export"
        if(success):
            success = self.on_pre_export() is not False
            if(not success):
                self.failure_step = "on_pre_export"
        if(success):
            success = self.export() is not False
            if(not success):
                self.failure_step = "export"
        if(success):
            self.on_export() is not False
            if(not success):
                self.failure_step = "on_export"
        if(success):
            success = self.post_export() is not False
            if(not success):
                self.failure_step = "post_export"
        if(success):
            self.on_post_export() is not False
            if(not success):
                self.failure_step = "on_post_export"

        if(success):
            self.success()
            self.on_success()
        else:
            self.failure()
            self.on_failure()

        return success

    # -------------------------------------------------------------

    @abc.abstractmethod
    def export(self):
        """
        Base shared logic for export
        :return <bool:success> Has this step complete successfully?
        """
        pass

    def on_export(self):
        """
        Additional logic called after `export`. Put program specific logic here.
        """
        pass

    @abc.abstractmethod
    def pre_export(self):
        """
        Base shared logic called just before export
        :return <bool:success> Has this step complete successfully?
        """
        pass

    def on_pre_export(self):
        """
        Additional logic called after `pre_export`. Put program specific logic here.
        """
        pass

    @abc.abstractmethod
    def post_export(self):
        """
        Base shared logic called just after export
        :return <bool:success> Has this step complete successfully?
        """
        pass

    def on_post_export(self):
        """
        Additional logic called after `post_export`. Put program specific logic here.
        """
        pass

    # -------------------------------------------------------------

    @abc.abstractmethod
    def success(self):
        """
        Ran on a successful asset export
        """
        pass

    def on_success(self):
        """
        Ran after the `success` method. Put program specific logic here.
        """
        pass

    @abc.abstractmethod
    def failure(self):
        """
        Ran on a failed asset export
        """
        pass

    def on_failure(self):
        """
        Ran after the `failure` method. Put program specific logic here.
        """
        pass
