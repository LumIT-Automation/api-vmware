from typing import List

from vmware.repository.Stage2.Command import Command as Repository

from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class Command:
    def __init__(self, uid: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.uid = uid
        self.command: str = ""
        self.args: dict = {}

        self.__load()



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
            Repository.modify(self.uid, data)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.uid)
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
    def add(data: dict) -> None:
        try:
            Repository.add(data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.uid)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception:
            raise CustomException(status=400, payload={"SSH": "non existent command."})
