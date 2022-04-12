from typing import List
import io
import paramiko

from vmware.repository.Stage2.BoostrapKey import BootstrapKey as Repository
from vmware.helpers.Log import Log


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
        pubKey = ""
        keyType = ""
        privateKey = None
        try:
            keyStringIO = io.StringIO(self.priv_key)
            for cls in [paramiko.RSAKey, paramiko.ECDSAKey, paramiko.Ed25519Key, paramiko.DSSKey]:
                try:
                    privateKey = cls.from_private_key(keyStringIO)
                    keyType = privateKey.get_name()
                    break
                except paramiko.ssh_exception.SSHException:
                    # Wrong type, try the next one.
                    pass

            if privateKey:
                pubKey = keyType+' '+privateKey.get_base64()
        except Exception:
            pass

        return pubKey



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
