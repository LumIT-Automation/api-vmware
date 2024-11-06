from typing import List
from django.db import connection

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper


class Permission:

    # IdentityGroupRoleObject

    # Tables: group_role_object, identity_group, role, vmware_object



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    @staticmethod
    def get(permissionId: int) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM group_role_object WHERE id=%s", [permissionId])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "Non existent permission"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(permissionId: int, identityGroupId: int, roleId: int, objectId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("UPDATE group_role_object SET id_group=%s, id_role=%s, id_object=%s WHERE id=%s", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                objectId,
                permissionId
            ])
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"database": "Duplicated permission"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(id) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM group_role_object WHERE id = %s", [
                id
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> List[dict]:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT "
                "group_role_object.id, "
                "identity_group.name AS identity_group_name, "
                "identity_group.identity_group_identifier AS identity_group_identifier, "
                "role.role AS role, "
                "vmware_object.id AS object_id, vmware_object.moId, "
                "vmware_object.id_asset AS object_asset, "
                "vmware_object.name AS object_name, "
                "asset.fqdn AS asset_name "                                
                "FROM identity_group "
                "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                "LEFT JOIN role ON role.id = group_role_object.id_role "
                "LEFT JOIN `vmware_object` ON vmware_object.id = group_role_object.id_object "
                "INNER JOIN asset ON asset.id = `vmware_object`.id_asset "
                "WHERE role.role IS NOT NULL ")
            l = DBHelper.asDict(c)

            for el in l:
                el["object"] = {
                    "object_id": el["object_id"],
                    "id_asset": el["object_asset"],
                    "asset_name": el["asset_name"],
                    "moId": el["moId"],
                    "name": el["object_name"]
                }

                del(el["object_id"])
                del(el["object_asset"])
                del(el["asset_name"])
                del(el["moId"])
                del(el["object_name"])

            return l
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(identityGroupId: int, roleId: int, objectId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("INSERT INTO group_role_object (id, id_group, id_role, id_object) VALUES (NULL, %s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                objectId
            ])
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"database": "duplicated permission"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
