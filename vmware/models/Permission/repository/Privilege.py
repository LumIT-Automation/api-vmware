from typing import List
from django.db import connection

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper


class Privilege:

    # Table: privilege

    #   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #   `privilege` varchar(64) NOT NULL UNIQUE KEY,
    #   `privilege_type` enum('object-folder','object-network','object-datastore','asset','global') NOT NULL DEFAULT 'asset',
    #   `description` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM privilege WHERE id = %s", [id])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "non existent privilege"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



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



    @staticmethod
    def getType(privilege: str) -> str:
        c = connection.cursor()

        try:
            c.execute("SELECT privilege_type FROM privilege WHERE privilege = %s", [privilege])
            return DBHelper.columnAsList(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
