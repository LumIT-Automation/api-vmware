from typing import List, Dict, Union

from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.models.Stage2.Command import Command
from vmware.models.Stage2.TargetCommand import TargetCommand
from vmware.models.Stage2.TargetCommandExecution import TargetCommandExecution

from vmware.models.Stage2.repository.Target import Target as Repository

DataConnection: Dict[str, Union[str, int]] = {
    "ip":  "",
    "port": "",
    "api_type": "",
    "id_bootstrap_key": "",
    "username": "",
    "password": ""
}

class Target:
    def __init__(self, targetId: int, loadCommands: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(targetId)
        self.connection: DataConnection = None
        self.id_asset: int = 0
        self.task_moid: str = ""
        self.task_state: str = ""
        self.task_progress: int = 0
        self.task_startTime: str = ""
        self.task_queueTime: str = ""
        self.task_message: str = ""
        self.second_stage_state: str = ""
        self.vm_name: str = ""

        self.commands: List[dict] = [] # composition with Command and TargetCommand's user_args + id.
        self.commandsExecutions: List[TargetCommandExecution] = []

        self.__load(loadCommands)



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
            return BootstrapKey(self.connection["id_bootstrap_key"]).getPublic()
        except Exception as e:
            raise e



    def getPassword(self) -> str:
        try:
            return Repository.getPassword(self.id)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(maxResults: int, loadCommands: bool = True) -> List[dict]:
        try:
            o = Repository.list(maxResults)

            if loadCommands:
                for el in o:
                    el["commands"] = list()

                    targetCommands = TargetCommand.listTargetCommands(el["id"])
                    # "id": 1,
                    # "id_target": 1,
                    # "command": "ls",
                    # "user_args": {
                    #     "__path": "/"
                    # }

                    for targetCommand in targetCommands:
                        command = Command(targetCommand["command"]).repr()
                        # "uid": "ls",
                        # "command": "ls ${__path}",
                        # "template_args": {
                        #     "__path": "str"
                        # }

                        command["user_args"] = targetCommand["user_args"]
                        command["id_target_command"] = targetCommand["id"]

                        el["commands"].append(command)

                    el["commandsExecutions"] = TargetCommandExecution.listTargetCommandExecutions(el["id"])

            return o
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

    def __load(self, loadCommands: bool) -> None:
        try:
            info = Repository.get(self.id)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)

            if loadCommands:
                targetCommands = TargetCommand.listTargetCommands(self.id)
                for targetCommand in targetCommands:
                    command = Command(targetCommand["command"]).repr()

                    command["user_args"] = targetCommand["user_args"]
                    command["id_target_command"] = targetCommand["id"]
                    self.commands.append(command)

                self.commandsExecutions = TargetCommandExecution.listTargetCommandExecutions(self.id)
        except Exception as e:
            raise e
