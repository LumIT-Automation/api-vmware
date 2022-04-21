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
    #   `id` int(11) NOT NULL AUTO_INCREMENT,
    #   `id_target` int(11) NOT NULL,
    #   `command` varchar(64) NOT NULL DEFAULT '',
    #   `user_args` varchar(8192) NOT NULL DEFAULT '{}'



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def delete(id: int) -> None:
        c = connections[TargetCommand.db].cursor()

        if TargetCommand.__exists(id):
            try:
                c.execute("DELETE FROM target_command WHERE id = %s", [
                    id
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
                "ORDER BY id ASC ", [
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
    def __exists(id: int) -> int:
        c = connections[TargetCommand.db].cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM target_command WHERE id = %s", [
                id
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
