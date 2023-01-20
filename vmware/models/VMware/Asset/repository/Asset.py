from typing import List

from django.utils.html import strip_tags
from django.db import connection
from django.db import transaction

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Asset:

    # Table: asset

    #   `id` int(11) NOT NULL,
    #   `address` varchar(64) NOT NULL,
    #   `port` int(11) DEFAULT NULL,
    #   `fqdn` varchar(255) DEFAULT NULL,
    #   `baseurl` varchar(255) NOT NULL,
    #   `tlsverify` tinyint(4) NOT NULL DEFAULT 1,
    #   `datacenter` varchar(255) DEFAULT NULL,
    #   `environment` varchar(255) NOT NULL,
    #   `position` varchar(255) DEFAULT NULL,
    #   `api_type` varchar(64) NOT NULL DEFAULT '',
    #   `api_additional_data` varchar(255) NOT NULL DEFAULT '',
    #   `username` varchar(64) NOT NULL DEFAULT '',
    #   `password` varchar(64) NOT NULL DEFAULT ''



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM asset WHERE id = %s", [
                assetId
            ])

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(assetId: int, data: dict) -> None:
        assetId = int(assetId)
        sql = ""
        values = []
        c = connection.cursor()

        if Asset.__exists(assetId):
            # Build SQL query according to dict fields.
            for k, v in data.items():
                sql += k+"=%s,"
                values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute("UPDATE asset SET "+sql[:-1]+" WHERE id = "+str(assetId), # user data are filtered by the serializer.
                    values
                )

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent VMware endpoint"})



    @staticmethod
    def delete(assetId: int) -> None:
        c = connection.cursor()

        if Asset.__exists(assetId):
            try:
                c.execute("DELETE FROM asset WHERE id = %s", [
                    assetId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
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
            c.execute("SELECT id, address, fqdn, baseurl, tlsverify, api_type, datacenter, environment, position FROM asset")
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
        c = connection.cursor()

        # Build SQL query according to dict fields.
        for k, v in data.items():
            s += "%s,"
            keys += k+","
            values.append(strip_tags(v)) # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO asset "+keys+" VALUES ("+s[:-1]+")", # user data are filtered by the serializer.
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
    def __exists(assetId: int) -> int:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM asset WHERE id = %s", [
                assetId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
