from typing import List

from vmware.models.Stage2.repository.Command import Command as Repository

from vmware.helpers.Exception import CustomException


class Command:
    def __init__(self, uid: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.uid = uid
        self.command: str = ""
        self.template_args: dict = {}
        self.reserved: int = 0

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
            if not self.reserved:
                Repository.modify(self.uid, data)
            else:
                raise CustomException(status=400, payload={"database": "reserved command not modifiable."})
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            if not self.reserved:
                Repository.delete(self.uid)
            else:
                raise CustomException(status=400, payload={"database": "reserved command not modifiable."})
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
