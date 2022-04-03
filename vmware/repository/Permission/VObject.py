from django.db import connection
from typing import List
from django.utils.html import strip_tags

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class VObject:

    # Table: vmware_object`

    #   `id` int(11) NOT NULL,
    #   `id_asset` int(11) NOT NULL,
    #   `moId` varchar(64) NOT NULL,
    #   `name` varchar(255) NOT NULL,
    #   `description` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int, moId: str) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM `vmware_object` WHERE `moId` = %s AND id_asset = %s", [
                moId,
                assetId
            ])
            info = DBHelper.asDict(c)[0]

            # VMware object type.
            info["object_type"] = VmwareHelper.getType(moId)

            return info
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(id: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM `vmware_object` WHERE id = %s", [
                id
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> List[dict]:
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
    def modify(id: int, data: dict) -> None:
        sql = ""
        values = []
        c = connection.cursor()

        if VObject.__exists(id):
            # %s placeholders and values for SET.
            for k, v in data.items():
                sql += k + "=%s,"
                values.append(strip_tags(v)) # no HTML allowed.

            # Condition for WHERE.
            values.append(id)

            try:
                c.execute("UPDATE `vmware_object` SET "+sql[:-1]+" WHERE id = %s",
                    values
                )
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": "Vmware object not found in db."})



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



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __exists(id: int) -> int:
        c = connection.cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM `vmware_object` WHERE id = %s", [
                id
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
