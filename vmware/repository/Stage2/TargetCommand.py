from typing import List

from django.utils.html import strip_tags
from django.db import connections

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class TargetCommand:
    db = 'stage2'

    # Table: target_command
    #   `id` int(11) NOT NULL,
    #   `id_target` int(11) NOT NULL,
    #   `command` varchar(64) NOT NULL DEFAULT '',
    #   `args` varchar(8192) DEFAULT NULL;




    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(targetId: int) -> dict:
        c = connections[TargetCommand.db].cursor()

        try:
            c.execute("SELECT * FROM target_command "
                      "WHERE target_command.id = %s ", [
                        targetId
                    ])

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()




    @staticmethod
    def modify(tCommandId: int, data: dict) -> None:
        sql = ""
        values = []
        c = connections[TargetCommand.db].cursor()

        if TargetCommand.__exists(tCommandId):
            # Build the update query according to dict fields.
            for k, v in data.items():
                if v is None:
                    sql += k+"=DEFAULT,"
                else:
                    sql += k+"=%s,"
                    values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute(
                    "UPDATE target SET "+sql[:-1]+" WHERE id = "+str(tCommandId),
                    values
                )
            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def delete(targetId: int) -> None:
        c = connections[TargetCommand.db].cursor()

        if TargetCommand.__exists(targetId):
            try:
                c.execute("DELETE FROM target_command WHERE id = %s", [
                    targetId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def list(targetId: int) -> List[dict]:
        c = connections[TargetCommand.db].cursor()

        try:
            c.execute(
                "SELECT * "
                "FROM target_command "
                "WHERE id_target = %s", [
                    targetId
            ])
            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> int:
        s = ""
        keys = "("
        values = []
        c = connections[TargetCommand.db].cursor()

        # Build SQL query according to dict fields.
        for k, v in data.items():
            if v:
                s += "%s,"
                keys += k + ","
                values.append(strip_tags(v)) # no HTML allowed.
        keys = keys[:-1]+")"

        try:
            c.execute("INSERT INTO target_command "+keys+" VALUES ("+s[:-1]+")",
                values
            )

            return c.lastrowid
        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    @staticmethod
    def __exists(targetId: int) -> int:
        c = connections[TargetCommand.db].cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM target_command WHERE id = %s", [
                targetId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
