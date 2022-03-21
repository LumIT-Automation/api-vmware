from typing import List

from dataclasses import dataclass
from vmware.models.Stage2.BoostrapKey import BootstrapKey

from vmware.repository.Stage2.Target import Target as Repository
from vmware.helpers.Log import Log

@dataclass
class DataConnection:
    ip: str
    port: int
    api_type: str
    keyId: int
    username: str
    password: str



class Target:
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(targetId)
        self.connectionData: DataConnection = None

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.id, data)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id)
        except Exception as e:
            raise e



    def getBootstrapPubKey(self) -> str:
        try:
            t = Repository.get(self.id)
            Log.log(t, '_')
            # bootStrapKey = BootstrapKey(t["connectionData"]["id_bootstrap_key "])
            bootStrapKey = BootstrapKey(1)
            pubKey = bootStrapKey.getPublic()
            Log.log(pubKey, '_')
            return pubKey

        except Exception as e:
            raise e


    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> List[dict]:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            aId = Repository.add(data)

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.id)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception:
            pass
