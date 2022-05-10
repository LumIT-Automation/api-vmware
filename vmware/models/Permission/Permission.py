from vmware.models.Permission.Role import Role
from vmware.models.Permission.VObject import VObject
from vmware.models.Permission.Privilege import Privilege
from vmware.models.VMware.FolderVM import FolderVM

from vmware.repository.Permission.Permission import Permission as Repository

from vmware.helpers.VMware.VmwareHelper import VmwareHelper


class Permission:

    # IdentityGroupRoleObject

    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        self.identity_group_identifier: int
        self.identity_group_name: str
        self.role: str
        self.obj = VObject



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroupId: int, role: str, vmwareObject: VObject) -> None:
        try:
            if role == "admin":
                moId = "any" # if admin: override to "any".
                objectId = VObject(vmwareObject.id_asset, moId).id # get the id of object "any".
            else:
                moId = vmwareObject.moId
                objectId = vmwareObject.id

            if not objectId:
                if moId != "any":
                    # If the VMObject does not exist (in the db), create it.
                    objectId = VObject.add(
                        moId=moId,
                        assetId=vmwareObject.id_asset,
                        objectName=vmwareObject.name
                    )

            Repository.modify(
                self.id,
                identityGroupId,
                Role(name=role).id,
                objectId
            )
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
                    VmwareHelper.getType(moId), # vmware object type from the moId.
                    assetId,
                    moId
                )
            )
        except Exception as e:
            raise e



    # Get all the moId of the objects on which the user has a privilege. Use sets to deduplicate.
    # Use this with actions of privilege_type = 'object-%'
    # (for privilege_type = 'global' or 'asset' hasUserPermission is the right choice).
    @staticmethod
    def allowedObjectsSet(groups: list, action: str, assetId: int = 0) -> set:
        # Superadmin's group.
        for gr in groups:
            if gr.lower() == "automation.local":
                return {"any"}

        try:
            objectMoIdSet = Repository.allowedObjectsByPrivilegeSet(groups=groups, action=action, assetId=assetId)
            privilegeType = Privilege.getType(action)
            if privilegeType == "object-folder": # for folder permissions allow the access for the subFolders also.
                subItems = set()
                for objMoId in objectMoIdSet:
                    subTree = FolderVM.folderTreeQuick(assetId=assetId, folderMoId=objMoId)[0]["children"]
                    subItems.update(FolderVM.treeToSet(subTree, moIdSet=None))
                objectMoIdSet.update(subItems)

            return objectMoIdSet
        except Exception as e:
            raise e



    @staticmethod
    def rawList() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(identityGroupId: int, role: str, vmwareObject: VObject) -> None:
        try:
            if role == "admin":
                moId = "any" # if admin: override to "any".
                objectId = VObject(vmwareObject.id_asset, moId).id # get the id of object "any".
            else:
                moId = vmwareObject.moId
                objectId = vmwareObject.id

            if not objectId:
                if moId != "any":
                    # If the VMObject does not exist (in the db), create it.
                    objectId = VObject.add(
                        moId=moId,
                        assetId=vmwareObject.id_asset,
                        objectName=vmwareObject.name
                    )

            Repository.add(
                identityGroupId,
                Role(name=role).id,
                objectId
            )
        except Exception as e:
            raise e
