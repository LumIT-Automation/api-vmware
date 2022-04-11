from typing import List, Dict, Union

from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.models.Stage2.Command import Command
from vmware.models.Stage2.TargetCommand import TargetCommand

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
        self.task_state: str = ""
        self.task_progress: int = 0
        self.task_startTime: str = ""
        self.task_queueTime: str = ""
        self.task_message: str = ""
        self.vm_name: str = ""

        self.commands: List[Command] = []

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def repr(self) -> dict:
        out = {
            "commands": list()
        }

        try:
            o = vars(self)
            for el in o["commands"]:
                out["commands"].append(el.repr())

            o["commands"] = out["commands"] # replace.

            return o
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
            o = Repository.list()
            for el in o:
                el["commands"] = list()

                commands = TargetCommand.listTargetCommands(el["id"])
                for command in commands:
                    el["commands"].append(Command(command["command"]).repr())

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

    def __load(self) -> None:
        try:
            info = Repository.get(self.id)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)

            commands = TargetCommand.listTargetCommands(self.id)
            for command in commands:
                self.commands.append(Command(command["command"]))
        except Exception as e:
            raise e
