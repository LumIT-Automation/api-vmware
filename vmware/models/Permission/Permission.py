from vmware.models.Permission.Role import Role
from vmware.models.Permission.VMObject import VMObject

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

    def modify(self, identityGroupId: int, role: str, assetId: int, moId: str, objectType: str, name: str="") -> None:
        c = connection.cursor()

        if self.permissionId:
            try:
                # RoleId.
                r = Role(roleName=role)
                roleId = r.info()["id"]

                if role == "admin":
                    moId = "any"  # if admin: "any" is the only valid choice (on selected assetId).
                    objectType = "any_type"

                # Get the VMObject id. If the VMObject does not exist in the db, create it.
                o = VMObject(assetId=assetId, moId=moId, objectType=objectType)
                try:
                    objectId = o.info()["id"]
                except Exception:
                    objectId = VMObject.add(moId=moId, assetId=assetId, objectName=name, objectType=objectType)

                c.execute("UPDATE group_role_object SET id_group=%s, id_role=%s, id_object=%s WHERE id=%s", [
                    identityGroupId, # AD or RADIUS group.
                    roleId,
                    objectId,
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
    def hasUserPermission(groups: list, action: str, assetId: int = 0, objectId: str = "", object_type: str = "") -> bool:
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
                    assetWhere = "AND vmObject.id_asset = %s "

                if objectId:
                    objectWhere = "AND ( vmObject.moId = 'any' "  # if "any" appears in the query results so far -> pass.
                    if object_type == "folder":
                            f = VMFolder(assetId, objectId)
                            foldersMoIdsList = f.parentList()
                            foldersMoIdsList.append(objectId)
                            objectWhere += "OR (vmObject.moId = 'any_f' " # "any_f" == any folder -> pass.
                            for moId in foldersMoIdsList:
                                args.append(moId)
                                objectWhere += "OR vmObject.moId = %s "
                            objectWhere += ") "
                    elif object_type == "datastore":
                        objectWhere += "OR (vmObject.moId = 'any_d' OR vmObject.moId = %s) " # "any_d" == any datastore -> pass.
                        args.append(objectId)
                    elif object_type == "network":
                        objectWhere += "OR (vmObject.moId = 'any_n' OR vmObject.moId = %s) " # "any_n" == any network -> pass.
                        args.append(objectId)
                    else:
                        raise CustomException(status=400, payload={"database": "\"object_type\" can have only one of these values: folder,datastore,network"})
                    objectWhere += ") "

                args.append(action)

                query = ("SELECT COUNT(*) AS count "
                        "FROM identity_group "
                        "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                        "LEFT JOIN role_privilege ON role_privilege.id_role = group_role_object.id_role "
                        "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                        "LEFT JOIN vmObject ON vmObject.id = group_role_object.id_object "
                       
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
                    "vmObject.id AS object_id, vmObject.moId, "
                    "vmObject.id_asset AS object_asset, "
                    "vmObject.name AS object_name, "
                    "vmObject.object_type "
                                    
                    "FROM identity_group "
                    "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                    "LEFT JOIN role ON role.id = group_role_object.id_role "
                    "LEFT JOIN `vmObject` ON vmObject.id = group_role_object.id_object "
                    "WHERE role.role IS NOT NULL ")
            l = DBHelper.asDict(c)

            for el in l:
                el["object"] = {
                    "object_id": el["object_id"],
                    "asset_id": el["object_asset"],
                    "moId": el["moId"],
                    "name": el["object_name"],
                    "object_type": el["object_type"]
                }

                del(el["object_id"])
                del(el["object_asset"])
                del(el["moId"])
                del(el["object_name"])
                del(el["object_type"])

            return {
                "items": l
            }

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(identityGroupId: int, role: str, assetId: int, moId: str, objectType: str, name: str = "") -> None:
        c = connection.cursor()

        try:
            # RoleId.
            r = Role(roleName=role)
            roleId = r.info()["id"]

            if role == "admin":
                moId = "any" # if admin: "any" is the only valid choice (on selected assetId).
                objectType = "any_type"

            # Get the VMObject id. If the VMObject does not exist in the db, create it.
            o = VMObject(assetId=assetId, moId=moId, objectType=objectType)
            try:
                objectId = o.info()["id"]
            except Exception:
                objectId = VMObject.add(moId=moId, assetId=assetId, objectName=name, objectType=objectType)

            c.execute("INSERT INTO group_role_object (id, id_group, id_role, id_object) VALUES (NULL, %s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                objectId
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
