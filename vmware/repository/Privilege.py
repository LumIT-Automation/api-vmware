from typing import List
from django.db import connection

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Privilege:

    # Table: privilege

    #   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #   `privilege` varchar(64) NOT NULL UNIQUE KEY,
    #   `privilege_type` enum('object','asset','global') NOT NULL DEFAULT 'object',
    #   `description` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> List[dict]:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM privilege")
            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
