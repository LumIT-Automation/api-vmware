from typing import List

from django.utils.html import strip_tags
from django.db import connections
from django.db import transaction

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class FinalPubKey:
    db = 'stage2'

    # Table: final_pubkey
    #   `id` int(11) NOT NULL,
    #   `comment` varchar(1024) NOT NULL DEFAULT '',
    #   `pub_key` varchar(2048) NOT NULL DEFAULT '';



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(keyId: int) -> dict:
        c = connections[FinalPubKey.db].cursor()

        try:
            c.execute("SELECT * FROM final_pubkey "
                      "WHERE id = %s ", [
                        keyId
                    ])

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(keyId: int, data: dict) -> None:
        sql = ""
        values = []
        c = connections[FinalPubKey.db].cursor()

        if FinalPubKey.__exists(keyId):
            # Build SQL query according to dict fields.
            for k, v in data.items():
                if v is None:
                    sql += k+"=DEFAULT,"
                else:
                    sql += k+"=%s,"
                    values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute("UPDATE final_pubkey SET "+sql[:-1]+" WHERE id = "+str(int(keyId)),
                    values
                )

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def delete(keyId: int) -> None:
        c = connections[FinalPubKey.db].cursor()

        if FinalPubKey.__exists(keyId):
            try:
                c.execute("DELETE FROM final_pubkey WHERE id = %s", [
                    keyId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def list() -> List[dict]:
        c = connections[FinalPubKey.db].cursor()

        try:
            c.execute("SELECT * FROM final_pubkey")
            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> int:
        s = ""
        keys = "("
        values = []
        c = connections[FinalPubKey.db].cursor()

        # Build SQL query according to dict fields.
        for k, v in data.items():
            s += "%s,"
            keys += k+","
            values.append(strip_tags(v)) # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO final_pubkey "+keys+" VALUES ("+s[:-1]+")",
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
    def __exists(keyId: int) -> int:
        c = connections[FinalPubKey.db].cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM final_pubkey WHERE id = %s", [
                keyId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
