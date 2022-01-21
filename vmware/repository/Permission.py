from django.db import connection

from vmware.models.VMware.VMFolder import VMFolder

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Permission:

    # IdentityGroupRoleObject

    def __init__(self, id: int, groupId: int = 0, roleId: int = 0, partitionId: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id

        self.id_group = groupId
        self.id_role = roleId
        self.id_partition = partitionId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

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
                            f = VMFolder(assetId, objectMoId)
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
    def listIdentityGroupsRolesPartitions() -> list:
        c = connection.cursor()

        try:
            c.execute("SELECT "
                    "group_role_object.id, "
                    "identity_group.name AS identity_group_name, "
                    "identity_group.identity_group_identifier AS identity_group_identifier, "
                    "role.role AS role, "
                    "vmware_object.id AS object_id, vmware_object.moId, "
                    "vmware_object.id_asset AS object_asset, "
                    "vmware_object.name AS object_name, "
                    "(CASE SUBSTRING_INDEX(vmware_object.moId, '-', 1) "
                            "WHEN 'group' THEN 'folder' "
                            "WHEN 'datastore' THEN 'datastore' "
                            "WHEN 'network' THEN 'network' "
                            "WHEN 'dvportgroup' THEN 'network' "
                    "END) AS object_type "              
                                    
                    "FROM identity_group "
                    "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                    "LEFT JOIN role ON role.id = group_role_object.id_role "
                    "LEFT JOIN `vmware_object` ON vmware_object.id = group_role_object.id_object "
                    "WHERE role.role IS NOT NULL ")
            return DBHelper.asDict(c)
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
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
