from typing import List

from vmware.models.Permission.repository.Privilege import Privilege as Repository


class Privilege:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        self.privilege: str
        self.privilege_type: str
        self.description: str



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def getType(privilege: str) -> str:
        try:
            return Repository.getPrivType(privilege)
        except Exception as e:
            raise e



    @staticmethod
    def list() -> List[dict]:
        try:
            return Repository.list()
        except Exception as e:
            raise e
