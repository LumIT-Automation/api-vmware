from vmware.models.Permission.Role import Role
from vmware.models.Permission.VMObject import VMObject

from vmware.helpers.Exception import CustomException

from vmware.repository.Permission import Permission as Repository


class Permission:

    # IdentityGroupRoleObject

    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        self.identity_group_identifier: int
        self.identity_group_name: str
        self.role: str
        self.obj = VMObject



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroupId: int, role: str, vmwareObject: VMObject) -> None:
        try:
            if role == "admin":
                # If admin: "any" is the only valid choice (on selected assetId).
                moId = "any"
            else:
                moId = vmwareObject.moId

            # Get the VMObject id. If the VMObject does not exist in the db, create it.
            o = VMObject(assetId=vmwareObject.id_asset, moId=vmwareObject.moId)

            try:
                objectId = o.info()["id"]
            except Exception:
                objectId = VMObject.add(
                    moId=moId,
                    assetId=vmwareObject.id_asset,
                    objectName=vmwareObject.name
                )

            if objectId:
                Repository.modify(
                    self.id,
                    identityGroupId,
                    Role(name=role).info()["id"],
                    objectId
                )
            else:
                raise CustomException(status=400, payload={"database": "Object not added: wrong object type?"})
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
    def hasUserPermission(groups: list, action: str, assetId: int = 0, moId: str = "") -> bool:
        # Superadmin's group.
        for gr in groups:
            if gr.lower() == "automation.local":
                return True

        try:
            return bool(
                Repository.countUserPermissions(
                    groups,
                    action,
                    VMObject.getType(moId), # vmware object type from the moId.
                    assetId,
                    moId
                )
            )
        except Exception as e:
            raise e



    @staticmethod
    def rawList() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(identityGroupId: int, role: str, vmwareObject: VMObject) -> None:
        try:
            if role == "admin":
                # If admin: "any" is the only valid choice (on selected assetId).
                moId = "any"
            else:
                moId = vmwareObject.moId

            # Get the VMObject id. If the VMObject does not exist in the db, create it.
            o = VMObject(assetId=vmwareObject.id_asset, moId=vmwareObject.moId)

            try:
                objectId = o.info()["id"]
            except Exception:
                objectId = VMObject.add(
                    moId=moId,
                    assetId=vmwareObject.id_asset,
                    objectName=vmwareObject.name
                )

            if objectId:
                Repository.add(
                    identityGroupId,
                    Role(name=role).info()["id"],
                    objectId
                )
            else:
                raise CustomException(status=400, payload={"database": "Object not added: wrong object type?"})
        except Exception as e:
            raise e
