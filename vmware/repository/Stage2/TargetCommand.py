import json
from typing import List

from django.utils.html import strip_tags
from django.db import connections

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class TargetCommand:
    db = 'stage2'

    # Table: target_command
    #   `id_target` int(11) NOT NULL,
    #   `command` varchar(64) NOT NULL DEFAULT '',
    #   `user_args` varchar(8192) NOT NULL DEFAULT '{}',
    #   `sequence` int(11) NOT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def delete(targetId: int, commandUid: str) -> None:
        c = connections[TargetCommand.db].cursor()

        if TargetCommand.__exists(targetId, commandUid):
            try:
                c.execute("DELETE FROM target_command WHERE id_target = %s AND command = %s", [
                    targetId, commandUid
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
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
                "WHERE id_target = %s "
                "ORDER BY sequence ", [
                    targetId
            ])
            o = DBHelper.asDict(c)
            for l in o:
                if "user_args" in l:
                    l["user_args"] = json.loads(l["user_args"])

            return o
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> int:
        s = ""
        keys = "("
        values = []
        c = connections[TargetCommand.db].cursor()

        if "user_args" in data:
            data["user_args"] = json.dumps(data["user_args"])

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
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    @staticmethod
    def __exists(targetId: int, commandUid: str) -> int:
        c = connections[TargetCommand.db].cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM target_command WHERE id_target = %s AND command = %s", [
                targetId, commandUid
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
