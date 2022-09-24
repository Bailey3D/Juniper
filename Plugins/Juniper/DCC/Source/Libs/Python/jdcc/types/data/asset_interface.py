import json
import os

import juniper.types.misc.guid


class AssetInterface(object):
    def __init__(self, asset_path, create_if_invalid=False):
        """
        Class used for interfacing with asset metadata files (Ie, .geometry, .material, etc)
        :param <str:asset_path> The path to the asset file
        :param [<bool:create_if_invalid>] If True, then the file will be created if it doesn't exist
        """
        self.__asset_path = asset_path
        self.__create_if_invalid = create_if_invalid

        self.__data_on_disk = None
        self.__data = None

        self.load(create_if_invalid=create_if_invalid)

    # ---------------------------------------------------------------

    def get_data(self):
        """
        Gets a read only version of the data
        :return <{str:value}:output> The dict
        """
        return self.__data

    @property
    def asset_path(self):
        """
        :return <str:path> Absolute path to the asset
        """
        return self.__asset_path

    @property
    def validity(self):
        """
        :return <bool:validity> True if this asset is valid - else False
        """
        return os.path.isfile(self.asset_path) or self.__create_if_invalid

    def load(self, create_if_invalid=False):
        """
        Loads the data in
        :param <bool:create_if_invalid> Should this file be created on save if it doesn't exist?
        """
        if(os.path.isfile(self.asset_path)):
            with open(self.asset_path, "r") as f:
                self.__data = json.load(f)
        else:
            self.__data = {}

        # make sure the asset has a guid if it's not set..
        if(not self.get_metadata_key("asset_guid")):
            self.set_metadata_key("asset_guid", str(juniper.types.misc.guid.Guid()))

    def save(self, force=False):
        """
        Saves the asset if it is dirty
        :param [<bool:force>] Should we force save even if the asset isn't dirty? This will force the revision guid to update.
        """
        if(self.dirty or force):
            self.set_metadata_key("revision_guid", str(juniper.types.misc.guid.Guid()))
            if(not os.path.isdir(os.path.dirname(self.asset_path))):
                os.makedirs(os.path.dirname(self.asset_path))
            with open(self.asset_path, "w") as f:
                json.dump(self.__data, f, indent=4)
            return True
        return False

    @property
    def dirty(self):
        """
        Gets whether the asset is dirty (if it has altered from the version saved to disk)
        :return <bool:dirty> True if dirty - else False
        """
        return self.__data_on_disk != self.__data

    # ---------------------------------------------------------------

    def get_key(self, key, group):
        """
        Gets a key on this asset under a given group
        :param <str:key> The name of the key to get
        :param [<str:subgroup>] The target subgroup to get - defaults to None
        :return <value:output> The value of the key if found - else None
        """
        if(group in self.__data):
            if(key in self.__data[group]):
                return self.__data[group][key]
        return None

    def set_key(self, key, value, group):
        """
        Sets a key on this asset under a given group
        :param <str:key> The name of the key to set
        :param <value:value> The value to set the key to
        :param [<str:subgroup>] The target subgroup to set this for - defaults to None or "metadata"
        """
        if(group not in self.__data):
            self.__data[group] = {}
        self.__data[group][key] = value

    def get_key_names(self, group):
        """
        Gets all keys from the given group
        :param <str:group> The group to get the keys for
        :return <[str]:keys> All keys if the group exists, else None
        """
        if(group in self.__data):
            return list(self.__data[group].keys())
        return {}

    def get_group_data(self, group):
        """
        Gets the dict data for an entire group if it exists
        :param <str:group> The group to get
        :return <{str:value}:output> The group dict if it exists - else None
        """
        if(group in self.__data):
            return self.__data[group]
        return {}

    # ---------------------------------------------------------------

    def get_metadata_key(self, key, subgroup=None):
        """
        Gets a metadata key on this asset
        :param <str:key> The name of the key to get
        :param [<str:subgroup>] The target subgroup to get - defaults to None
        :return <value:output> The value of the key if found - else None
        """
        metadata_key = "metadata"
        if(subgroup):
            metadata_key = f"metadata:{subgroup}"
        if(metadata_key in self.__data):
            if(key in self.__data[metadata_key]):
                return self.__data[metadata_key][key]
        return None

    def set_metadata_key(self, key, value, subgroup=None):
        """
        Sets a metadata key on this asset
        :param <str:key> The name of the key to set
        :param <value:value> The value to set the key to
        :param [<str:subgroup>] The target subgroup to set this for - defaults to None or "metadata"
        """
        metadata_key = "metadata"
        if(subgroup):
            metadata_key = f"metadata:{subgroup}"
        if(metadata_key not in self.__data):
            self.__data[metadata_key] = {}
        self.__data[metadata_key][key] = value

    # ---------------------------------------------------------------

    @property
    def asset_guid(self):
        """
        :return <str:guid> The guid as stored in the asset json
        """
        return self.get_metadata_key("asset_guid")

    @property
    def revision_guid(self):
        """
        :return <str:guid> The revision guid as stored in the asset json
        """
        if(not self.get_metadata_key("revision_guid")):
            self.update_revision_guid()
        return self.get_metadata_key("revision_guid")

    def update_revision_guid(self):
        """
        Updates the revision guid for this asset
        """
        self.set_metadata_key(
            "revision_guid",
            str(juniper.types.misc.guid.Guid())
        )
