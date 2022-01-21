from django.db import connection

from vmware.models.VMware.VMFolder import VMFolder as vCemterVMFolder
from vmware.models.VMware.Network import Network as vCenterNetwork
from vmware.models.VMware.Datastore import Datastore as vCenterDatastore

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log



class VMObject:
    def __init__(self, assetId: int, moId: str, name: str = "", description: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = None
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
            c.execute("SELECT COUNT(*) AS c, id FROM `vmware_object` WHERE `moId` = %s AND id_asset = %s", [
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
        objectType = ""

        c = connection.cursor()
        try:
            c.execute("SELECT * FROM `vmware_object` WHERE `moId` = %s AND id_asset = %s", [
                self.moId,
                self.assetId
            ])

            info = DBHelper.asDict(c)[0]
            moIdPrefix = self.moId.split('-')[0]
            if moIdPrefix == "group":
                objectType = "folder"
            elif moIdPrefix == "datastore":
                objectType = "datastore"
            elif moIdPrefix == "network" or moIdPrefix == "dvportgroup":
                objectType = "network"

            info["object_type"] = objectType
            return info

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def delete(self) -> None:
        c = connection.cursor()
        try:
            c.execute("DELETE FROM `vmware_object` WHERE `moId` = %s AND id_asset = %s", [
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
            c.execute("SELECT *, "
                        "(CASE SUBSTRING_INDEX(vmware_object.moId, '-', 1) "
                            "WHEN 'group' THEN 'folder' "
                            "WHEN 'datastore' THEN 'datastore' "
                            "WHEN 'network' THEN 'network' "
                            "WHEN 'dvportgroup' THEN 'network' "
                        "END) AS object_type "
                      "FROM vmware_object")

            return {
                "items": DBHelper.asDict(c)
            }

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(moId: str, assetId: int, objectName: str, objectType: str, description: str = "") -> int:
        object_id = ""
        object_name = ""
        c = connection.cursor()

        # Check if the objectName is exists in the vCenter server. Skip for "any".
        if moId == "any":
            object_id = "any"
            object_name = "any"
        else:
            if objectType == 'folder':
                vCentervmObjects = vCemterVMFolder.list(assetId)["items"]
                for v in vCentervmObjects:
                    if v["moId"] == moId and v["name"] == objectName:
                        object_id = v["moId"]
                        object_name = v["name"]
                        break
            elif objectType == 'network':
                vCentervmObjects = vCenterNetwork.list(assetId)["items"]
                for n in vCentervmObjects:
                    if n["moId"] == moId and n["name"] == objectName:
                        object_id = n["moId"]
                        object_name = n["name"]
                        break
            elif objectType == 'datastore':
                vCentervmObjects = vCenterDatastore.list(assetId)["items"]
                for d in vCentervmObjects:
                    if d["moId"] == moId and d["name"] == objectName:
                        object_id = d["moId"]
                        object_name = d["name"]
                        break

        if not object_id:
            raise CustomException(status=400, payload={"VMware": "Object with given moId and name not found in vCenter"})

        try:
            c.execute("INSERT INTO `vmware_object` (`id`, `moId`, `id_asset`, `name`, `description`) VALUES (NULL, %s, %s, %s, %s)", [
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
