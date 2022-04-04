from typing import List

from vmware.repository.Stage2.FinalPubKey import FinalPubKey as Repository
from vmware.helpers.Log import Log


class FinalPubKey:
    def __init__(self, keyId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(keyId)
        self.pub_key: str = ""
        self.comment: str = ""

        self.__load()

        # To POST an ssh private key, grab the output of the command:
        # cat id_rsa | sed -e 's/$/\\n/g' | tr -d '\n'



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
