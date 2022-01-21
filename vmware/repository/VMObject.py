from django.db import connection
from typing import Callable

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class VMObject:

    # Table: vmware_object`

    #   `id` int(11) NOT NULL,
    #   `moId` varchar(64) NOT NULL,
    #   `id_asset` int(11) NOT NULL,
    #   `name` varchar(255) NOT NULL,
    #   `description` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int, moId: str, getType: Callable[[str], str]) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM `vmware_object` WHERE `moId` = %s AND id_asset = %s", [
                moId,
                assetId
            ])
            info = DBHelper.asDict(c)[0]

            # VMware object type.
            info["object_type"] = getType(moId)

            return info
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(assetId: int, moId: str) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM `vmware_object` WHERE `moId` = %s AND id_asset = %s", [
                moId,
                assetId
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> list:
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

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(assetId: int, moId: str, objectName: str, description: str) -> int:
        c = connection.cursor()

        try:
            c.execute("INSERT INTO `vmware_object` (`id`, `moId`, `id_asset`, `name`, `description`) VALUES (NULL, %s, %s, %s, %s)", [
                moId,
                assetId,
                objectName,
                description
            ])

            return c.lastrowid
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
