from typing import List
import json

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
            o = DBHelper.asDict(c)
            for l in o:
                if "args" in l:
                    l["args"] = json.loads(l["args"])

            return o
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

        if "args" in data:
            data["args"] = json.dumps(data["args"])

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
