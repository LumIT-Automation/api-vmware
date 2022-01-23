from django.db import connection
from typing import List

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Role:

    # Table: role

    #   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #   `role` varchar(64) NOT NULL UNIQUE KEY,
    #   `description` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(role: str) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM role WHERE role = %s", [
                role
            ])

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list(showPrivileges: bool = False) -> List[dict]:
        c = connection.cursor()

        try:
            if showPrivileges:
                # Grouping roles' and privileges' values into two columns.
                j = 0
                c.execute(
                    "SELECT role.*, IFNULL(group_concat(DISTINCT privilege.privilege), '') AS privileges "
                    "FROM role "
                    "LEFT JOIN role_privilege ON role_privilege.id_role = role.id "
                    "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                    "GROUP BY role.role"
                )

                items = DBHelper.asDict(c)
                for ln in items:
                    if "privileges" in items[j]:
                        if "," in ln["privileges"]:
                            items[j]["privileges"] = ln["privileges"].split(",")
                        else:
                            if ln["privileges"]:
                                items[j]["privileges"] = [ ln["privileges"] ]
                    j = j+1
            else:
                c.execute("SELECT * FROM role")
                items = DBHelper.asDict(c)

            return items
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
