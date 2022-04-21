from typing import List

from vmware.repository.Stage2.TargetCommandExecution import TargetCommandExecution as Repository

from vmware.helpers.Log import Log


class TargetCommandExecution:
    def __init__(self, targetCommandExecId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = targetCommandExecId
        self.id_target_command: int = 0
        self.timestamp: str = ""
        self.exit_status: int = 0
        self.stdout: str = ""
        self.stderr: str = ""



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listTargetCommandExecutions(targetId: int) -> List[dict]:
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
