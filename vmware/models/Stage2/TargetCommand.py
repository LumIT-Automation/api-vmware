from typing import List

from vmware.repository.Stage2.TargetCommand import TargetCommand as Repository

from vmware.helpers.Log import Log


class TargetCommand:
    def __init__(self, targetId: int, commandUid: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id_target: int = int(targetId)
        self.command: str = commandUid
        self.args: dict = {}
        self.sequence: int = 0



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def delete(self) -> None:
        try:
            Repository.delete(self.id_target, self.command)
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
