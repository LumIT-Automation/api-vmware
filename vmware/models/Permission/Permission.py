from vmware.models.Permission.Role import Role
from vmware.models.Permission.VMFolder import VMFolder

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

    def modify(self, identityGroupId: int, role: str, assetId: int, vmFolderName: str) -> None:
        c = connection.cursor()

        if self.permissionId:
            try:
                if role == "admin":
                    vmFolderName = "any" # if admin: "any" is the only valid choice (on selected assetId).

                # RoleId.
                r = Role(roleName=role)
                roleId = r.info()["id"]

                # VMFolder id. If vmFolder does not exist, create it.
                p = VMFolder(assetId=assetId, vmFolderName=vmFolderName)
                if p.exists():
                    vmFolderId = p.info()["id"]
                else:
                    vmFolderId = p.add(assetId, vmFolderName)

                c.execute("UPDATE group_role_vmFolder SET id_group=%s, id_role=%s, id_vmFolder=%s WHERE id=%s", [
                    identityGroupId, # AD or RADIUS group.
                    roleId,
                    vmFolderId,
                    self.permissionId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()



    def delete(self) -> None:
        c = connection.cursor()

        if self.permissionId:
            try:
                c.execute("DELETE FROM group_role_vmFolder WHERE id = %s", [
                    self.permissionId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def hasUserPermission(groups: list, action: str, assetId: int = 0, vmFolderName: str = "") -> bool:
        if action and groups:
            args = groups.copy()
            assetWhere = ""
            vmFolderWhere = ""
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
                    assetWhere = "AND `vmFolder`.id_asset = %s "

                if vmFolderName:
                    args.append(vmFolderName)
                    vmFolderWhere = "AND (`vmFolder`.`vmFolder` = %s OR `vmFolder`.`vmFolder` = 'any') " # if "any" appears in the query results so far -> pass.

                args.append(action)

                c.execute("SELECT COUNT(*) AS count "
                    "FROM identity_group "
                    "LEFT JOIN group_role_vmFolder ON group_role_vmFolder.id_group = identity_group.id "
                    "LEFT JOIN role ON role.id = group_role_vmFolder.id_role "
                    "LEFT JOIN role_privilege ON role_privilege.id_role = role.id "
                    "LEFT JOIN `vmFolder` ON `vmFolder`.id = group_role_vmFolder.id_vmFolder "                      
                    "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                    "WHERE ("+groupWhere[:-4]+") " +
                    assetWhere +
                    vmFolderWhere +
                    "AND privilege.privilege = %s ",
                        args
                )
                q = DBHelper.asDict(c)[0]["count"]
                if q:
                    return bool(q)

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()

        return False



    @staticmethod
    def list() -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT "
                      "group_role_vmFolder.id, "
                      "identity_group.name AS identity_group_name, "
                      "identity_group.identity_group_identifier AS identity_group_identifier, "
                      "role.role AS role, "
                      "`vmFolder`.id_asset AS vmFolder_asset, "
                      "`vmFolder`.`vmFolder` AS vmFolder_name "
                "FROM identity_group "
                "LEFT JOIN group_role_vmFolder ON group_role_vmFolder.id_group = identity_group.id "
                "LEFT JOIN role ON role.id = group_role_vmFolder.id_role "
                "LEFT JOIN `vmFolder` ON `vmFolder`.id = group_role_vmFolder.id_vmFolder "
                "WHERE role.role IS NOT NULL")
            l = DBHelper.asDict(c)

            for el in l:
                el["vmFolder"] = {
                    "asset_id": el["vmFolder_asset"],
                    "name": el["vmFolder_name"]
                }

                del(el["vmFolder_asset"])
                del(el["vmFolder_name"])

            return {
                "items": l
            }

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    @staticmethod
    def add(identityGroupId: int, role: str, assetId: int, vmFolderName: str) -> None:
        c = connection.cursor()

        try:
            if role == "admin":
                vmFolderName = "any" # if admin: "any" is the only valid choice (on selected assetId).

            # RoleId.
            r = Role(roleName=role)
            roleId = r.info()["id"]

            # VMFolder id. If vmFolder does not exist, create it.
            p = VMFolder(assetId=assetId, vmFolderName=vmFolderName)
            if p.exists():
                vmFolderId = p.info()["id"]
            else:
                vmFolderId = p.add(assetId, vmFolderName)

            c.execute("INSERT INTO group_role_vmFolder (id_group, id_role, id_vmFolder) VALUES (%s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                vmFolderId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    @staticmethod
    def cleanup(identityGroupId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM group_role_vmFolder WHERE id_group = %s", [
                identityGroupId,
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()
