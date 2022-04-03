from typing import List

from vmware.repository.Permission.Role import Role as Repository


class Role:
    def __init__(self, id: int = 0, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = id
        self.role: str = name
        self.description: str

        self.__load()



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



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.role)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception:
            pass
