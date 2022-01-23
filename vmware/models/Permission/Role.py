from typing import List

from vmware.repository.Role import Role as Repository


class Role:
    def __init__(self, id: int = 0, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = id
        self.role: str = name
        self.description: str



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Repository.get(self.role)
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
    def listWithPrivileges() -> List[dict]:
        try:
            return Repository.list(True)
        except Exception as e:
            raise e
