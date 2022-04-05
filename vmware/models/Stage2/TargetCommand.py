from typing import List, Dict, Union

from vmware.models.Stage2.BoostrapKey import BootstrapKey

from vmware.repository.Stage2.TargetCommand import TargetCommand as Repository

from vmware.helpers.Utils import GroupConcatToDict
from vmware.helpers.Log import Log


class TargetCommand:
    def __init__(self, tCommandId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(tCommandId)
        self.id_target: int = 0
        self.command: str = ""
        self.args: str = ""

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Repository.get(self.id)
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



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(targetId: int) -> List[dict]:
        try:
            return Repository.list(targetId)
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
        except Exception:
            pass
