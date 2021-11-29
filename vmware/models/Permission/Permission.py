from vmware.models.Permission.Role import Role
from vmware.models.Permission.VMFolder import VMFolder as VMFolderPermission

from vmware.models.VMware.VMFolder import VMFolder

from django.db import connection
from django.conf import settings

from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper



class Permission:
    def __init__(self, permissionId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.permissionId = permissionId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroupId: int, role: str, assetId: int, moId: str, name: str="") -> None:
        c = connection.cursor()

        if self.permissionId:
            try:
                # RoleId.
                r = Role(roleName=role)
                roleId = r.info()["id"]

                if role == "admin":
                    moId = "any"  # if admin: "any" is the only valid choice (on selected assetId).
                else:
                    # VMFolderPermission id. If vmFolder does not exist, create it.
                    f = VMFolderPermission(assetId=assetId, moId=moId)
                    if not f.exists():
                        VMFolderPermission.add(moId, assetId, name)

                c.execute("UPDATE group_role_object SET id_group=%s, id_role=%s, id_asset=%s, id_object=%s WHERE id=%s", [
                    identityGroupId, # AD or RADIUS group.
                    roleId,
                    assetId,
                    moId,
                    self.permissionId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()



    def delete(self) -> None:
        c = connection.cursor()

        if self.permissionId:
            try:
                c.execute("DELETE FROM group_role_object WHERE id = %s", [
                    self.permissionId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def hasUserPermission(groups: list, action: str, assetId: int = 0, objectId: str="") -> bool:
        if action and groups:
            args = groups.copy()
            assetWhere = ""
            objectWhere = ""
            c = connection.cursor()

            # Superadmin's group.
            for gr in groups:
                if gr.lower() == "automation.local":
                    return True

            try:
                # Build the first half of the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)
                groupWhere = ''
                for g in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                # Put all the args of the query in a list.
                if assetId:
                    args.append(assetId)
                    assetWhere = "AND group_role_object.id_asset = %s "

                if objectId:
                    f = VMFolder(assetId, objectId)
                    foldersMoIdsList = f.parentList()
                    objectWhere = "AND (vmFolder.moId = 'any' " # if "any" appears in the query results so far -> pass.
                    for moId in foldersMoIdsList:
                        args.append(moId)
                        objectWhere += "OR vmFolder.moId = %s "
                    objectWhere += ") "

                args.append(action)

                query = ("SELECT COUNT(*) AS count "
                        "FROM identity_group "
                        "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                        "LEFT JOIN role_privilege ON role_privilege.id_role = group_role_object.id_role "
                        "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                        "LEFT JOIN asset ON asset.id = group_role_object.id_asset "
                        "LEFT JOIN vmFolder ON vmFolder.moId = group_role_object.id_object "
                       
                    "WHERE ("+groupWhere[:-4]+") " +
                    assetWhere +
                    objectWhere +
                    "AND privilege.privilege = %s "
                )

                Log.log(query, '_')
                c.execute(query, args)
                q = DBHelper.asDict(c)[0]["count"]
                if q:
                    return bool(q)

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        return False



    @staticmethod
    def list() -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT "
                    "group_role_object.id, "
                    "identity_group.name AS identity_group_name, "
                    "identity_group.identity_group_identifier AS identity_group_identifier, "
                    "role.role AS role, "
                    "vmFolder.moId AS object_id, "
                    "vmFolder.id_asset AS object_asset, "
                    "vmFolder.name AS object_name "
                                    
                    "FROM identity_group "
                    "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                    "LEFT JOIN role ON role.id = group_role_object.id_role "
                    "LEFT JOIN `vmFolder` ON vmFolder.moId = group_role_object.id_object AND vmFolder.id_asset = group_role_object.id_asset "
                    "WHERE role.role IS NOT NULL ")
            l = DBHelper.asDict(c)

            for el in l:
                el["object"] = {
                    "asset_id": el["object_asset"],
                    "moId": el["object_id"],
                    "name": el["object_name"]
                }

                del(el["object_asset"])
                del (el["object_id"])
                del(el["object_name"])

            return {
                "items": l
            }

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(identityGroupId: int, role: str, assetId: int, moId: str, name: str="") -> None:
        c = connection.cursor()

        try:
            # RoleId.
            r = Role(roleName=role)
            roleId = r.info()["id"]

            if role == "admin":
                moId = "any" # if admin: "any" is the only valid choice (on selected assetId).
            else:
                # VMFolderPermission id. If vmFolder does not exist, create it.
                f = VMFolderPermission(assetId=assetId, moId=moId, name=name)
                if not f.exists():
                    VMFolderPermission.add(moId, assetId, name)

            c.execute("INSERT INTO group_role_object (id, id_group, id_role, id_asset, id_object) VALUES (NULL, %s, %s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                assetId,
                moId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def cleanup(identityGroupId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM group_role_object WHERE id_group = %s", [
                identityGroupId,
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
