from django.db import connection
from typing import List

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper


class Role:

    # Table: role

    #   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #   `role` varchar(64) NOT NULL UNIQUE KEY,
    #   `description` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int, role: str) -> dict:
        c = connection.cursor()

        try:
            if id:
                c.execute("SELECT * FROM role WHERE id = %s", [id])
            if role:
                c.execute("SELECT * FROM role WHERE role = %s", [role])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "non existent role"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> List[dict]:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM role")

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
