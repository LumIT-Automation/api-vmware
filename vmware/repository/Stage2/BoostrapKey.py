import base64
import logging
from typing import List

from django.utils.html import strip_tags
from django.db import connections
from django.db import transaction

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class BootstrapKey:
    db = 'stage2'

    # Table: stage2_target
    #   `id` int(11) NOT NULL,
    #   `priv_key` varchar(8192) NOT NULL DEFAULT '',
    #   `comment` varchar(1024) NOT NULL DEFAULT ''



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(keyId: int) -> dict:
        c = connections[BootstrapKey.db].cursor()

        try:
            c.execute("SELECT * FROM bootstrap_key "
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
        c = connections[BootstrapKey.db].cursor()

        if BootstrapKey.__exists(keyId):
            try:
                if "priv_key" in data:
                    data["priv_key"] = base64.b64decode(data["priv_key"]).decode('utf-8')

                # Build SQL query according to dict fields.
                for k, v in data.items():
                    if v is None:
                        sql += k+"=DEFAULT,"
                    else:
                        sql += k+"=%s,"
                        values.append(strip_tags(v)) # no HTML allowed.

                logging.disable(logging.WARNING) # do not ever log private key.
                c.execute("UPDATE bootstrap_key SET "+sql[:-1]+" WHERE id = "+str(keyId),
                    values
                )
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                logging.disable(logging.NOTSET) # re-enable django logging.
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def delete(keyId: int) -> None:
        c = connections[BootstrapKey.db].cursor()

        if BootstrapKey.__exists(keyId):
            try:
                c.execute("DELETE FROM bootstrap_key WHERE id = %s", [
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
        c = connections[BootstrapKey.db].cursor()

        try:
            c.execute("SELECT * FROM bootstrap_key")
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
        c = connections[BootstrapKey.db].cursor()

        try:
            if "priv_key" in data:
                data["priv_key"] = base64.b64decode(data["priv_key"]).decode('utf-8')

            # Build SQL query according to dict fields.
            for k, v in data.items():
                s += "%s,"
                keys += k+","
                values.append(strip_tags(v)) # no HTML allowed.
            keys = keys[:-1]+")"

            logging.disable(logging.WARNING) # do not ever log private key.
            with transaction.atomic():
                c.execute("INSERT INTO bootstrap_key "+keys+" VALUES ("+s[:-1]+")",
                    values
                )
                return c.lastrowid
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            logging.disable(logging.NOTSET) # Re-enable django logging.
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    @staticmethod
    def __exists(keyId: int) -> int:
        c = connections[BootstrapKey.db].cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM bootstrap_key WHERE id = %s", [
                keyId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
