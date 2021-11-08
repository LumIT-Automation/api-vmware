from django.utils.html import strip_tags
from django.db import connection
from django.db import transaction

from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper



class Asset:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def vmwareDataConnection(self) -> dict:
        dataConnection = dict()
        c = connection.cursor()

        try:
            c.execute("SELECT `id`, `address`, `port`, `api_type`, `api_additional_data`, `username`, `password` "
                    "FROM asset WHERE id = %s", [
                self.assetId
            ])

            a = DBHelper.asDict(c)[0]

            if a["api_type"] == "Vmware":
                    dataConnection = {
                        "ip": a["address"],
                        "port": a["port"],
                        "additional_data": a["api_additional_data"],
                        "username": a["username"],
                        "password": a["password"]
                    }

            else:
                raise CustomException(status=404, payload={"asset": "Wrong api_type (not vmware)"})

            return dataConnection

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def info(self) -> dict:
        a = dict()
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM asset WHERE id = %s", [
                self.assetId
            ])

            a = DBHelper.asDict(c)[0]
            a["auth"] = {
                "username": a["username"],
                "password": a["password"],
            }

            del(
                a["username"],
                a["password"]
            )

            return a

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    def modify(self, data: dict) -> None:
        sql = ""
        values = []

        c = connection.cursor()

        if self.__exists():
            # Build SQL query according to dict fields.
            for k, v in data.items():
                sql += k+"=%s,"
                values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute("UPDATE asset SET "+sql[:-1]+" WHERE id = "+str(self.assetId),
                    values
                )

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": {"message": "Non existent VMware endpoint"}})



    def delete(self) -> None:
        c = connection.cursor()

        if self.__exists():
            try:
                c.execute("DELETE FROM asset WHERE id = %s", [
                    self.assetId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": {"message": "Non existent VMware endpoint"}})



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> dict:
        c = connection.cursor()
        try:
            c.execute("SELECT id, address, fqdn, baseurl, tlsverify, datacenter, environment, position FROM asset")

            return dict({
                "data": {
                    "items": DBHelper.asDict(c)
                }
            })

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> None:
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
                c.execute("INSERT INTO asset "+keys+" VALUES ("+s[:-1]+")",
                    values
                )
                aId = c.lastrowid

                # When inserting an asset, add the "any" vmFolder (Permission).
                from vmware.models.Permission.VMFolder import VMFolder as PermissionVMFolder
                PermissionVMFolder.add(aId, "any")

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __exists(self) -> int:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM asset WHERE id = %s", [
                self.assetId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])

        except Exception:
            return 0
        finally:
            c.close()
