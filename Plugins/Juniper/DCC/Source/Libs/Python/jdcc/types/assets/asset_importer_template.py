"""
Abstract class for an asset importer
"""
import abc


class AssetImporterTemplate(object, metaclass=abc.ABCMeta):
    def __init__(self, asset_path):
        """
        Abstracted base class for asset importers
        :param <str:asset_path> The path to the asset to import
        """
        self.__asset_path = asset_path
        self.failure_step = None

    @property
    def asset_path(self):
        return self.__asset_path

    # ----------------------------------------------------------------

    @abc.abstractmethod
    def validate(self):
        """
        Validates whether the importer can run with the current settings
        :return <bool:valid> True if the exporter can be ran - else False
        """
        pass

    def execute(self):
        """
        Runs the importer
        :return <bool:success> True if the importer ran successfully - else False
        """
        success = self.validate()
        if(not success):
            self.failure_step = "validation"

        if(success):
            success = self.pre_import() is not False
            if(not success):
                self.failure_step = "pre_import"
        if(success):
            success = self.on_pre_import() is not False
            if(not success):
                self.failure_step = "on_pre_import"
        if(success):
            success = self.do_import() is not False
            if(not success):
                self.failure_step = "do_import"
        if(success):
            success = self.on_do_import() is not False
            if(not success):
                self.failure_step = "on_do_import"
        if(success):
            success = self.post_import() is not False
            if(not success):
                self.failure_step = "post_import"
        if(success):
            success = self.on_post_import() is not False
            if(not success):
                self.failure_step = "on_post_import"

        if(success):
            self.success()
            self.on_success()
        else:
            self.failure()
            self.on_failure()

        return success

    # ----------------------------------------------------------------

    @abc.abstractmethod
    def do_import(self):
        """
        Runs the base import logic.
        Would love to call this just `import` but cannot for obvious reasons..
        :return <bool:success> Has this step complete successfully?
        """
        pass

    def on_do_import(self):
        """
        Additional logic called after `do_import`. Put program specific logic here.
        """
        pass

    @abc.abstractmethod
    def pre_import(self):
        """
        Base shared logic called just before import
        :return <bool:success> Has this step complete successfully?
        """
        pass

    def on_pre_import(self):
        """
        Additional logic called after `pre_import`. Put program specific logic here.
        """
        pass

    @abc.abstractmethod
    def post_import(self):
        """
        Base shared logic called just after import
        :return <bool:success> Has this step complete successfully?
        """
        pass

    def on_post_import(self):
        """
        Additional logic called after `post_import`. Put program specific logic here.
        """
        pass

    # ----------------------------------------------------------------

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
        print(self.failure_step)

    def on_failure(self):
        """
        Ran after the `failure` method. Put program specific logic here.
        """
        pass
