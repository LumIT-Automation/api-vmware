from typing import List, Dict, Union

from vmware.models.Stage2.BoostrapKey import BootstrapKey

from vmware.repository.Stage2.Target import Target as Repository

from vmware.helpers.Log import Log


DataConnection: Dict[str, Union[str, int]] = {
    "ip":  "",
    "port": "",
    "api_type": "",
    "id_bootstrap_key": "",
    "username": "",
    "password": ""
}

class Target:
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(targetId)
        self.connection: DataConnection = None
        self.id_asset: int = 0
        self.task_moid: str = ""
        self.task_progress: int = 0
        self.task_startTime: str = ""
        self.task_queueTime: str = ""
        self.vm_name: str = ""

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def repr(self) -> dict:
        try:
            return vars(self)
        except Exception as e:
            raise e



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
            bootStrapKey = BootstrapKey(t["connectionData"]["id_bootstrap_key"])
            pubKey = bootStrapKey.getPublic()
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
    def add(data: dict) -> int:
        try:
            return Repository.add(data)
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
        except Exception as e:
            raise e
