from typing import List

from vmware.repository.Stage2.TargetCommand import TargetCommand as Repository

from vmware.helpers.Log import Log


class TargetCommand:
    def __init__(self, targetCommandId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = targetCommandId
        self.id_target: int = 0
        self.command: str = ""
        self.user_args: dict = {}



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def delete(self) -> None:
        try:
            Repository.delete(self.id)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listTargetCommands(targetId: int) -> List[dict]:
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
