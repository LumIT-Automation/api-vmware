import json
from typing import List

from django.utils.html import strip_tags
from django.db import connections

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Target:
    db = 'stage2'

    # Table: stage2_target



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(targetId: int) -> dict:
        c = connections[Target.db].cursor()

        try:
            c.execute("SELECT * FROM target WHERE target.id = %s ", [
                targetId
            ])

            o = DBHelper.asDict(c)[0]
            o["connection"] = {
                "ip": o["ip"],
                "port": o["port"],
                "api_type": o["api_type"],
                "id_bootstrap_key": o["id_bootstrap_key"],
                "username": o["username"]
            }

            del(o["ip"])
            del(o["port"])
            del(o["api_type"])
            del(o["id_bootstrap_key"])
            del(o["username"])

            return o
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def getPassword(targetId: int) -> str:
        c = connections[Target.db].cursor()

        try:
            c.execute("SELECT password FROM target WHERE target.id = %s ", [
                targetId
            ])

            return DBHelper.asDict(c)[0]["password"]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(targetId: int, data: dict) -> None:
        targetId = int(targetId)
        sql = ""
        values = []
        c = connections[Target.db].cursor()

        if "connection" in data:
            for el in ("ip", "port", "api_type", "id_bootstrap_key", "username"):
                if el in data["connection"]:
                    data[el] = data["connection"][el]
            del(data["connection"])

        if Target.__exists(targetId):
            # Build the update query according to dict fields.
            for k, v in data.items():
                if v is None:
                    sql += k+"=DEFAULT,"
                else:
                    sql += k+"=%s,"
                    values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute(
                    "UPDATE target SET "+sql[:-1]+" WHERE id = "+str(targetId), # user data are filtered by the serializer.
                    values
                )
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def delete(targetId: int) -> None:
        c = connections[Target.db].cursor()

        if Target.__exists(targetId):
            try:
                c.execute("DELETE FROM target WHERE id = %s", [
                    targetId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def list(maxResults: int) -> List[dict]:
        limit = ""
        c = connections[Target.db].cursor()

        if maxResults:
            limit = "LIMIT "+str(int(maxResults))

        try:
            c.execute(
                "SELECT * "
                "FROM target ORDER BY id DESC "+limit)

            o = DBHelper.asDict(c)
            for el in o:
                el["connection"] = {
                    "ip": el["ip"],
                    "port": el["port"],
                    "api_type": el["api_type"],
                    "id_bootstrap_key": el["id_bootstrap_key"],
                    "username": el["username"]
                }

                del(el["ip"])
                del(el["port"])
                del(el["api_type"])
                del(el["id_bootstrap_key"])
                del(el["username"])

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
        c = connections[Target.db].cursor()

        if "connection" in data:
            for el in ("ip", "port", "api_type", "id_bootstrap_key", "username"):
                if el in data["connection"]:
                    data[el] = data["connection"][el]
            del(data["connection"])

        # Build SQL query according to dict fields.
        for k, v in data.items():
            if v:
                s += "%s,"
                keys += k + ","
                values.append(strip_tags(v)) # no HTML allowed.
        keys = keys[:-1]+")"

        try:
            c.execute("INSERT INTO target "+keys+" VALUES ("+s[:-1]+")", # user data are filtered by the serializer.
                values
            )
            targetId = c.lastrowid

            return targetId
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    @staticmethod
    def __exists(targetId: int) -> int:
        c = connections[Target.db].cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM target WHERE id = %s", [
                targetId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
