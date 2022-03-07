from typing import List

from django.utils.html import strip_tags
from django.db import connection
from django.db import transaction

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Target:

    # Table: stage2_target
    #   `id` int(11) NOT NULL,
    #   `address` varchar(
    #   `port` int(11) DEFAULT NULL,
    #   `api_type` varchar(64) NOT NULL DEFAULT '',
    #   `id_bootstrap_key` int(11) DEFAULT NULL,
    #   `username` varchar(64) NOT NULL DEFAULT '',
    #   `password` varchar(64) NOT NULL DEFAULT ''

    # Table: stage2_bootstrap_key
    #   `id` int(11) NOT NULL,
    #   `key` varchar(8192) NOT NULL DEFAULT '',



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    @staticmethod
    def get(targetId: int) -> dict:
        c = connection.cursor()
        o = dict()

        try:
            c.execute("SELECT * FROM stage2_target "
                      "LEFT JOIN stage2_bootstrap_key ON stage2_bootstrap_key.id = stage2_target.id_bootstrap_key"
                      "WHERE stage2_target.id = %s ", [
                        targetId
                    ])

            a = DBHelper.asDict(c)[0]
            if a["api_type"] == "vmware":
                o["connectionData"] = a

                return o
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(targetId: int, data: dict) -> None:
        sql = ""
        values = []
        c = connection.cursor()

        if Target.__exists(targetId):
            # Build SQL query according to dict fields.
            for k, v in data.items():
                sql += k+"=%s,"
                values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute("UPDATE stage2_target SET "+sql[:-1]+" WHERE id = "+str(targetId),
                    values
                )

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent VMware endpoint"})



    @staticmethod
    def delete(targetId: int) -> None:
        c = connection.cursor()

        if Asset.__exists(targetId):
            try:
                c.execute("DELETE FROM stage2_target WHERE id = %s", [
                    assetId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent VMware endpoint"})



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> List[dict]:
        c = connection.cursor()

        try:
            c.execute("SELECT id, address, port, api_type FROM stage2_target")
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
        c = connection.cursor()

        # Build SQL query according to dict fields.
        for k, v in data.items():
            s += "%s,"
            keys += k+","
            values.append(strip_tags(v)) # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO stage2_target "+keys+" VALUES ("+s[:-1]+")",
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
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM stage2_target WHERE id = %s", [
                targetId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
