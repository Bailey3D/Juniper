import uuid
import hashlib
import secrets

import juniper
import juniper.types


class Guid(juniper.types.Object):
    def __init__(self, seed=None, guid=None):
        """
        Generates a random guid string
        :param [<object:seed>] The object to seed from - this is converted to a string and used
        :param [<str:guid>] Optional guid to force set as
        """
        if(guid):
            self.__guid = guid
        elif(seed):
            self.__guid = Guid.__generate_from_seed(seed)
        else:
            self.__guid = Guid.__generate_random()

    # ----------------------------------------------------------

    def __str__(self):
        return self.__guid

    # ----------------------------------------------------------

    @staticmethod
    def __generate_from_seed(seed):
        """
        Generates a guid string from an input seed
        :param <str:seed> The seed for the guid
        :return <str:guid> The guid string
        """
        hash_ = hashlib.md5()
        string_encoded = str(seed).encode("utf-8")
        hash_.update(string_encoded)
        hash_ = str(uuid.UUID(hash_.hexdigest()))
        hash_ = hash_.replace("-", "")
        return hash_

    @staticmethod
    def __generate_random():
        """
        Generates a guid string at random
        :return <str:guid> The guid string
        """
        return Guid.__generate_from_seed(secrets.token_hex(nbytes=16))
