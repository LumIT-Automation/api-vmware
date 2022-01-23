from typing import List

from vmware.repository.Privilege import Privilege as Repository


class Privilege:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        self.privilege = ""
        self.privilege_type = ""
        self.description = ""



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> List[dict]:
        try:
            return Repository.list()
        except Exception as e:
            raise e
