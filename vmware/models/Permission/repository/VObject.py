from django.db import connection
from typing import List

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.VMware.VmwareHelper import VmwareHelper


class VObject:

    # Table: vmware_object`



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int, assetId: int, moId: str) -> dict:
        c = connection.cursor()

        try:
            if id:
                c.execute("SELECT id, id_asset, moId, name, IFNULL (description, '') AS description FROM `vmware_object` WHERE `id` = %s", [id])
            if assetId and moId:
                c.execute("SELECT id, id_asset, moId, name, IFNULL (description, '') AS description FROM `vmware_object` WHERE `moId` = %s AND id_asset = %s", [moId, assetId])

            info = DBHelper.asDict(c)[0]
            info["object_type"] = VmwareHelper.getType(moId)

            return info
        except IndexError:
            raise CustomException(status=404, payload={"database": "Non existent object"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> List[dict]:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT id, id_asset, moId, name, IFNULL (description, '') AS description, "
                "IFNULL ((CASE SUBSTRING_INDEX(vmware_object.moId, '-', 1) "
                    "WHEN 'group' THEN 'folder' "
                    "WHEN 'datastore' THEN 'datastore' "
                    "WHEN 'network' THEN 'network' "
                    "WHEN 'dvportgroup' THEN 'network' "
                "END), '') AS object_type "
                "FROM vmware_object")

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(id: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM `vmware_object` WHERE id = %s", [id])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(assetId: int, moId: str, objectName: str, description: str) -> int:
        c = connection.cursor()

        try:
            c.execute(
                "INSERT INTO `vmware_object` (`id`, `moId`, `id_asset`, `name`, `description`) "
                "VALUES (NULL, %s, %s, %s, %s)", [
                    moId,
                    assetId,
                    objectName,
                    description
                ])

            return c.lastrowid
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"database": "Duplicated object"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
