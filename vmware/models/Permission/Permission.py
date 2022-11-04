from vmware.models.Permission.IdentityGroup import IdentityGroup
from vmware.models.Permission.Role import Role
from vmware.models.Permission.VObject import VObject
from vmware.models.Permission.Privilege import Privilege
from vmware.models.VMware.FolderVM import FolderVM

from vmware.models.Permission.repository.Permission import Permission as Repository

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHelper import VmwareHelper


class Permission:

    # IdentityGroupRoleObject

    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.identityGroup: IdentityGroup
        self.role: Role
        self.obj = VObject

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroup: IdentityGroup, role: Role, vmwareObject: VObject) -> None:
        try:
            Repository.modify(
                self.id,
                identityGroup.id,
                role.id,
                vmwareObject.id
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
                    try:
                        subTree = FolderVM.folderTreeQuick(assetId=assetId, folderMoId=objMoId)[0]["children"]
                        subItems.update(FolderVM.treeToSet(subTree, moIdSet=None))
                    except Exception:
                        pass
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
    def add(identityGroup: IdentityGroup, role: Role, vmwareObject: VObject) -> None:
        try:
            Repository.add(
                identityGroup.id,
                role.id,
                vmwareObject.id
            )
        except Exception as e:
            raise e



    @staticmethod
    def addFacade(identityGroupId: str, role: str, vmwareObjectInfo: dict) -> None:
        oAssetId = vmwareObjectInfo.get("assetId", "")
        oMoId = vmwareObjectInfo.get("moId", "")
        oName = vmwareObjectInfo.get("name", "")

        try:
            # Get existent or new object.
            if role == "admin":
                # Role admin -> "any" partition, which always exists.
                vmo = VObject(assetId=oAssetId, moId="any")
            else:
                try:
                    # Try retrieving object.
                    vmo = VObject(assetId=oAssetId, moId=oMoId)
                except CustomException as e:
                    if e.status == 404:
                        try:
                            # If object does not exist, create it (permissions database).
                            vmo = VObject(
                                id=VObject.add(
                                    moId=oMoId,
                                    assetId=oAssetId,
                                    objectName=oName
                                )
                            )
                        except Exception:
                            raise e
                    else:
                        raise e

            Permission.add(
                identityGroup=IdentityGroup(identityGroupIdentifier=identityGroupId),
                role=Role(role=role),
                vmwareObject=vmo
            )
        except Exception as e:
            raise e



    @staticmethod
    def modifyFacade(permissionId: int, identityGroupId: str, role: str, vmwareObjectInfo: dict) -> None:
        oAssetId = vmwareObjectInfo.get("assetId", "")
        oMoId = vmwareObjectInfo.get("moId", "")
        oName = vmwareObjectInfo.get("name", "")

        try:
            # Get existent or new object.
            if role == "admin":
                # Role admin -> "any" partition, which always exists.
                vmo = VObject(assetId=oAssetId, moId="any")
            else:
                try:
                    # Try retrieving object.
                    vmo = VObject(assetId=oAssetId, moId=oMoId)
                except CustomException as e:
                    if e.status == 404:
                        try:
                            # If object does not exist, create it (permissions database).
                            vmo = VObject(
                                id=VObject.add(
                                    moId=oMoId,
                                    assetId=oAssetId,
                                    objectName=oName
                                )
                            )
                        except Exception:
                            raise e
                    else:
                        raise e

            Permission(permissionId).modify(
                identityGroup=IdentityGroup(identityGroupIdentifier=identityGroupId),
                role=Role(role=role),
                vmwareObject=vmo
            )
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.id)

            self.identityGroup = IdentityGroup(id=info["id_group"])
            self.role = Role(id=info["id_role"])
            self.obj = VObject(id=info["id_object"])
        except Exception as e:
            raise e
