import json
from typing import List

from django.utils.html import strip_tags
from django.db import connections

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Command:
    db = 'stage2'

    # Table: command
    #   `uid` varchar(64) NOT NULL,
    #   `command` text NOT NULL,
    #   `template_args` varchar(8192) NOT NULL DEFAULT '{}'



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(uid: str) -> dict:
        c = connections[Command.db].cursor()

        try:
            c.execute("SELECT * FROM command WHERE uid = %s ", [
                uid
            ])

            o = DBHelper.asDict(c)[0]
            if "template_args" in o:
                o["template_args"] = json.loads(o["template_args"])

            return o
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(uid: str, data: dict) -> None:
        sql = ""
        values = []
        c = connections[Command.db].cursor()

        if "template_args" in data:
            data["template_args"] = json.dumps(data["template_args"])

        # %s placeholders and values for SET.
        for k, v in data.items():
            sql += k + "=%s,"
            values.append(strip_tags(v.replace('\r\n', '\n').replace('\r', '\n'))) # no HTML allowed, strip \r.

        # Condition for WHERE.
        values.append(uid)

        try:
            c.execute("UPDATE `command` SET "+sql[:-1]+" WHERE uid = %s",
                values
            )
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(uid: str) -> None:
        c = connections[Command.db].cursor()

        try:
            c.execute("DELETE FROM command WHERE uid = %s", [
                uid
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> List[dict]:
        c = connections[Command.db].cursor()

        try:
            c.execute("SELECT * FROM command")

            o = DBHelper.asDict(c)
            for l in o:
                if "template_args" in l:
                    l["template_args"] = json.loads(l["template_args"])

            return o
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> None:
        s = ""
        keys = "("
        values = []
        c = connections[Command.db].cursor()

        if "template_args" in data:
            data["template_args"] = json.dumps(data["template_args"])

        # Build SQL query according to dict fields.
        for k, v in data.items():
            s += "%s,"
            keys += k+","
            values.append(strip_tags(v.replace('\r\n', '\n').replace('\r', '\n'))) # no HTML allowed, strip \r.

        keys = keys[:-1]+")"

        try:
            c.execute("INSERT INTO command "+keys+" VALUES ("+s[:-1]+")",
                values
            )
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
