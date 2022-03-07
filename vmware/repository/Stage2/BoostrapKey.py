from typing import List

from django.utils.html import strip_tags
from django.db import connection
from django.db import transaction

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class BootstrapKey:

    # Table: stage2_target
    #   `id` int(11) NOT NULL,
    #   `priv_key` varchar(8192) NOT NULL DEFAULT '',



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    @staticmethod
    def modify(keyId: int, data: dict) -> None:
        sql = ""
        values = []
        c = connection.cursor()

        if BootstrapKey.__exists(keyId):
            # Build SQL query according to dict fields.
            for k, v in data.items():
                if v is None:
                    sql += k+"=DEFAULT,"
                else:
                    sql += k+"=%s,"
                    values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute("UPDATE stage2_bootstrap_key SET "+sql[:-1]+" WHERE id = "+str(keyId),
                    values
                )

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def delete(keyId: int) -> None:
        c = connection.cursor()

        if BootstrapKey.__exists(keyId):
            try:
                c.execute("DELETE FROM stage2_bootstrap_key WHERE id = %s", [
                    keyId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> List[dict]:
        c = connection.cursor()

        try:
            c.execute("SELECT id FROM stage2_bootstrap_key")
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

        Log.log("INSERT INTO stage2_bootstrap_key "+keys+" VALUES ("+s[:-1]+")", '_')
        try:
            with transaction.atomic():
                c.execute("INSERT INTO stage2_bootstrap_key "+keys+" VALUES ("+s[:-1]+")",
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
    def __exists(keyId: int) -> int:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM stage2_bootstrap_key WHERE id = %s", [
                keyId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
