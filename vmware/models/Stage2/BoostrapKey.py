from typing import List

from vmware.models.Stage2.repository.BoostrapKey import BootstrapKey as Repository

from vmware.helpers.Process import Process


class BootstrapKey:
    def __init__(self, keyId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(keyId)
        self.priv_key: str = ""
        self.pub_key: str = ""
        self.comment: str = ""

        self.__load()

        # To POST an ssh private key in json format, grab the output of the command:
        # cat ~/.ssh/id_rsa | base64 | tr -d '\n'



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



    def getPublic(self) -> str:
        pub_key = ""

        try:
            try:
                out = Process.execSSHKeygen(privateKey=self.priv_key)
                if out["success"]:
                    pub_key = out["stdout"].decode('utf-8').replace('\n', '')
            except ValueError:
                pub_key = "<error>"

            return pub_key
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> List[dict]:
        try:
            data = Repository.list()
            for el in data:
                bKey = BootstrapKey(keyId=el["id"])
                el["pub_key"] = bKey.getPublic()
                el["priv_key"] = "undisclosed"

            return data
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
