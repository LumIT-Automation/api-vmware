from vmware.models.Permission.Role import Role
from vmware.models.Permission.VMObject import VMObject
from vmware.models.Permission.Privilege import Privilege
from vmware.models.VMware.VirtualMachineFolder import VirtualMachineFolder

from vmware.helpers.Log import Log

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
                moId = "any" # if admin: override to "any".
                objectId = VMObject(vmwareObject.id_asset, moId).id # get the id of object "any".
            else:
                moId = vmwareObject.moId
                objectId = vmwareObject.id

            if not objectId:
                if moId != "any":
                    # If the VMObject does not exist (in the db), create it.
                    objectId = VMObject.add(
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
                    VMObject.getType(moId), # vmware object type from the moId.
                    assetId,
                    moId
                )
            )
        except Exception as e:
            raise e



    # List all the objects on which the user has a privilege.
    # Use this with list actions of privilege_type = 'object-%'
    # (for privilege_type = 'global' or 'asset' hasUserPermission is the right choice).
    @staticmethod
    def listAllowedObjects(groups: list, action: str, assetId: int = 0) -> list:
        objectList = []
        # Superadmin's group.
        for gr in groups:
            if gr.lower() == "automation.local":
                return ["any"]

        try:
            objectMoIdList = Repository.listAllowedObjectsByPrivilege(groups=groups, action=action, assetId=assetId)
            privilegeType = Privilege.getType(action)
            if privilegeType == 'object-folder': # for folder permissions allow also for the subFolders.
                for objMoId in objectMoIdList:
                    subTree = VirtualMachineFolder.folderTree(assetId=assetId, folderMoId=objMoId)[0]["folders"]
                    subFoldersMoIdList = []
                    VirtualMachineFolder.treeToList(subTree, moIdList=subFoldersMoIdList)
                    objectMoIdList.extend(subFoldersMoIdList)

            return objectMoIdList
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
                moId = "any" # if admin: override to "any".
                objectId = VMObject(vmwareObject.id_asset, moId).id # get the id of object "any".
            else:
                moId = vmwareObject.moId
                objectId = vmwareObject.id

            if not objectId:
                if moId != "any":
                    # If the VMObject does not exist (in the db), create it.
                    objectId = VMObject.add(
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
