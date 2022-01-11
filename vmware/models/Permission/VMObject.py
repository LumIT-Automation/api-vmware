from django.db import connection

from vmware.models.VMware.VMFolder import VMFolder as vCemterVMObject

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log



class VMObject:
    def __init__(self, assetId: int, moId: str, name: str = "", description: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.moId = moId
        self.name = name
        self.description = description



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exists(self) -> bool:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM `vmObject` WHERE `moId` = %s AND id_asset = %s", [
                self.moId,
                self.assetId
            ])
            o = DBHelper.asDict(c)

            return bool(int(o[0]['c']))

        except Exception:
            return False
        finally:
            c.close()



    def info(self) -> dict:
        c = connection.cursor()
        try:
            c.execute("SELECT * FROM `vmObject` WHERE `moId` = %s AND id_asset = %s", [
                self.moId,
                self.assetId
            ])

            return DBHelper.asDict(c)[0]

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def delete(self) -> None:
        c = connection.cursor()
        try:
            c.execute("DELETE FROM `vmObject` WHERE `moId` = %s AND id_asset = %s", [
                self.moId,
                self.assetId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> dict:
        c = connection.cursor()
        try:
            c.execute("SELECT * FROM vmObject")

            return {
                "items": DBHelper.asDict(c)
            }

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(moId: str, assetId: int, vmObject: str, description: str="") -> int:
        c = connection.cursor()

        # Check if the vmObject is exists in the vCenter server (skip for "any").
        if moId == "any":
            object_id = "any"
            object_name = "any"
        else:
            vCentervmObjects = vCemterVMObject.list(assetId)["items"]
            for v in vCentervmObjects:
                if v["moId"] == moId and v["name"] == vmObject:
                    object_id = v["moId"]
                    object_name = v["name"]

        try:
            c.execute("INSERT INTO `vmObject` (`moId`, `id_asset`, `name`, `description`) VALUES (%s, %s, %s, %s)", [
                object_id,
                assetId,
                object_name,
                description
            ])

            return c.lastrowid

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
