from typing import List

from dataclasses import dataclass

from vmware.repository.Stage2.Target import Target as Repository


@dataclass
class DataConnection:
    address: str
    port: int
    api_type: str
    key: str
    username: str
    password: str



class Target:
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(targetId)
        self.connectionData: DataConnection = None

        self.__load()



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
    def rawList() -> List[dict]:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            aId = Repository.add(data)

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
