from vmware.models.Permission.Role import Role
from vmware.models.Permission.VMObject import VMObject

from vmware.helpers.Exception import CustomException

from vmware.repository.Permission import Permission as Repository


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

    def modify(self, identityGroupId: int, role: str, assetId: int, moId: str, objectType: str, name: str = "") -> None:
        objectId = 0

        try:
            # RoleId.
            r = Role(roleName=role)
            roleId = r.info()["id"]

            if role == "admin":
                moId = "any" # if admin: "any" is the only valid choice (on selected assetId).
                objectType = ""

            # Get the VMObject id. If the VMObject does not exist in the db, create it.
            o = VMObject(assetId=assetId, moId=moId)

            try:
                objectInfo = o.info()
                if objectInfo["object_type"] == objectType: # also, check if the object has the right object type.
                    objectId = objectInfo["id"]
            except Exception:
                objectId = VMObject.add(moId=moId, assetId=assetId, objectName=name, objectType=objectType)

            if objectId:
                Repository.modify(self.id, identityGroupId, roleId, objectId)
            else:
                raise CustomException(status=400, payload={"database": "Object not added to the database (wrong object type?)"})
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def hasUserPermission(groups: list, action: str, assetId: int = 0, objectMoId: str = "") -> bool:
        # Superadmin's group.
        for gr in groups:
            if gr.lower() == "automation.local":
                return True

        try:
            return bool(
                Repository.countUserPermissions(
                    groups,
                    action,
                    VMObject.getType(objectMoId), # vmware object type from the moId.
                    assetId,
                    objectMoId
                )
            )
        except Exception as e:
            raise e



    @staticmethod
    def listIdentityGroupsRolesPartitions() -> list:
        try:
            l = Repository.listIdentityGroupsRolesPartitions()

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

            return l
        except Exception as e:
            raise e



    @staticmethod
    def add(identityGroupId: int, role: str, assetId: int, moId: str, objectType: str, name: str = "") -> None:
        objectId = 0

        try:
            # RoleId.
            r = Role(roleName=role)
            roleId = r.info()["id"]

            if role == "admin":
                moId = "any" # if admin: "any" is the only valid choice (on selected assetId).
                objectType = ""

            # Get the VMObject id. If the VMObject does not exist in the db, create it.
            o = VMObject(assetId=assetId, moId=moId)

            try:
                objectInfo = o.info()
                if objectInfo["object_type"] == objectType: # also, check if the object has the right object type.
                    objectId = objectInfo["id"]
            except Exception:
                objectId = VMObject.add(moId=moId, assetId=assetId, objectName=name, objectType=objectType)

            if objectId:
                Repository.add(identityGroupId, roleId, objectId)
            else:
                raise CustomException(status=400, payload={"database": "Object not added to the database (wrong object type?)"})
        except Exception as e:
            raise e
