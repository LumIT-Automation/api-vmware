from typing import List
from django.db import connection

from vmware.models.VMware.FolderVM import FolderVM

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Permission:

    # IdentityGroupRoleObject

    # Table: group_role_object

    #   `id` int(255) NOT NULL,
    #   `id_group` int(11) NOT NULL,
    #   `id_role` int(11) NOT NULL,
    #   `id_object` int(11) NOT NULL



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
            raise CustomException(status=404, payload={"database": "non existent permission"})
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
                        raise CustomException(status=400, payload={"database": "duplicated permission"})
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
    def countUserPermissions(groups: list, action: str, objectType: str, assetId: int = 0, objectMoId: str = "") -> int:
        if action and groups:
            args = groups.copy()
            assetWhere = ""
            objectWhere = ""

            c = connection.cursor()

            try:
                # Build the first half of the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)
                groupWhere = ''
                for g in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                # Put all the args of the query in a list.
                if assetId:
                    args.append(assetId)
                    assetWhere = "AND vmware_object.id_asset = %s "

                if objectMoId:
                    objectWhere = "AND ( vmware_object.moId = 'any' " # if "any" appears in the query results so far -> pass.
                    if objectType == "folder":
                            f = FolderVM(assetId, objectMoId)
                            foldersMoIdsList = f.parentList()
                            foldersMoIdsList.append(objectMoId)
                            objectWhere += "OR ("
                            for moId in foldersMoIdsList:
                                args.append(moId)
                                objectWhere += "vmware_object.moId = %s OR "
                            objectWhere = objectWhere[:-3]+") "
                    elif objectType == "datastore":
                        objectWhere += "OR (vmware_object.moId = %s) "
                        args.append(objectMoId)
                    elif objectType == "network":
                        objectWhere += "OR (vmware_object.moId = %s) "
                        args.append(objectMoId)
                    else:
                        raise CustomException(status=400, payload={"database": "\"object_type\" can have only one of these values: folder,datastore,network"})
                    objectWhere += ") "

                args.append(action)

                query = ("SELECT COUNT(*) AS count "
                        "FROM identity_group "
                        "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                        "LEFT JOIN role_privilege ON role_privilege.id_role = group_role_object.id_role "
                        "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                        "LEFT JOIN vmware_object ON vmware_object.id = group_role_object.id_object "
                       
                    "WHERE ("+groupWhere[:-4]+") " +
                    assetWhere +
                    objectWhere +
                    "AND privilege.privilege = %s "
                )

                c.execute(query, args)
                return DBHelper.asDict(c)[0]["count"]
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        return False



    @staticmethod
    def allowedObjectsByPrivilegeSet(groups: list, action: str, assetId: int = 0) -> set:
        if action and groups:
            args = groups.copy()
            groupWhere = ""
            assetWhere = ""

            c = connection.cursor()

            try:
                # Build the first half of the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)

                for g in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                # Put all the args of the query in a list.
                if assetId:
                    args.append(assetId)
                    assetWhere = "AND vmware_object.id_asset = %s "

                args.append(action)

                query = ("SELECT vmware_object.moId "
                        "FROM identity_group "
                        "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                        "LEFT JOIN role_privilege ON role_privilege.id_role = group_role_object.id_role "
                        "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                        "LEFT JOIN vmware_object ON vmware_object.id = group_role_object.id_object " 
                        "WHERE (" + groupWhere[:-4] + ") " +
                        assetWhere +
                        "AND "
                        "(vmware_object.moId = 'any' OR "
                        "CASE SUBSTRING_INDEX(privilege.privilege_type, '-', -1) "
                            "WHEN 'network' THEN ((SUBSTRING_INDEX(vmware_object.moId, '-', 1) = 'network') || (SUBSTRING_INDEX(vmware_object.moId, '-', 1) = 'dvportgroup')) "
                            "WHEN 'datastore' THEN (SUBSTRING_INDEX(vmware_object.moId, '-', 1) = 'datastore') "
                            "WHEN 'folder' THEN (SUBSTRING_INDEX(vmware_object.moId, '-', 1) = 'group') "
                        "END "
                        ") " 
                        "AND privilege.privilege = %s "
                )

                c.execute(query, args)
                return DBHelper.columnAsSet(c)
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()



    @staticmethod
    def list() -> List[dict]:
        c = connection.cursor()

        try:
            c.execute("SELECT "
                    "group_role_object.id, "
                    "identity_group.name AS identity_group_name, "
                    "identity_group.identity_group_identifier AS identity_group_identifier, "
                    "role.role AS role, "
                    "vmware_object.id AS object_id, vmware_object.moId, "
                    "vmware_object.id_asset AS object_asset, "
                    "vmware_object.name AS object_name "
                                    
                    "FROM identity_group "
                    "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                    "LEFT JOIN role ON role.id = group_role_object.id_role "
                    "LEFT JOIN `vmware_object` ON vmware_object.id = group_role_object.id_object "
                    "WHERE role.role IS NOT NULL ")
            l = DBHelper.asDict(c)

            for el in l:
                el["object"] = {
                    "object_id": el["object_id"],
                    "id_asset": el["object_asset"],
                    "moId": el["moId"],
                    "name": el["object_name"]
                }

                del(el["object_id"])
                del(el["object_asset"])
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
