from typing import List, Any

from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.vmware.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class VmwareHandler:
    contents = dict() # share content amongst all instances: do not re-fetch it during a "session".
    managedObjectCaches = dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.assetId = int(assetId)
        # self.moId = moId # VMware Managed Object Id.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    # Get VMware objects of type vimType.
    # vimTypes: vim.VirtualMachine, vim.Folder, vim.Datacenter, vim.VirtualApp, vim.ComputeResource, vim.Network, vim.Datastore.
    def getObjects(self, assetId: int, vimType: str, moId: str = "") -> List[Any]:
        obj = []

        try:
            if assetId not in VmwareHandler.contents:
                self.__fetchContent(assetId)

            if VmwareHandler.contents[assetId]:
                if moId:
                    # Return one moId (need an exact search here).
                    if moId in VmwareHandler.managedObjectCaches[assetId]:
                        # Search within the class "cache", first.
                        obj.append(VmwareHandler.managedObjectCaches[assetId][moId])
                    else:
                        c = VmwareHandler.contents[assetId].viewManager.CreateContainerView(VmwareHandler.contents[assetId].rootFolder, [vimType], True)
                        for managedObject_ref in c.view:
                            if managedObject_ref._GetMoId() == moId:
                                obj.append(managedObject_ref)

                                VmwareHandler.managedObjectCaches[assetId][moId] = managedObject_ref # put in "cache".
                                break
                else:
                    # Return complete list.
                    c = VmwareHandler.contents[assetId].viewManager.CreateContainerView(VmwareHandler.contents[assetId].rootFolder, [vimType], True)
                    for managedObject_ref in c.view:
                        obj.append(managedObject_ref)
            else:
                raise CustomException(status=400, payload={"VMware": "cannot fetch VMware objects."})
        except Exception as e:
            raise e

        return obj



    def getCustomizationSpecManager(self, assetId) -> object:
        try:
            if assetId not in VmwareHandler.contents:
                self.__fetchContent(assetId)

            return getattr(VmwareHandler.contents[assetId], "customizationSpecManager")
        except Exception as e:
            raise e



    def getTaskManager(self, assetId) -> object:
        try:
            #if not assetId in VmwareHandler.contents:
            #   self.__fetchContent(assetId)

            self.__fetchContent(assetId) # method used by Celery daemon: content gets outdated, so must be refreshed at every call.

            return getattr(VmwareHandler.contents[assetId], "taskManager")
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __fetchContent(self, assetId) -> None:
        try:
            supplicant = VmwareSupplicant(Asset(assetId))
            connection = supplicant.connect()

            Log.actionLog("Fetch VMware content.")
            VmwareHandler.contents[assetId] = connection.RetrieveContent()

            if assetId not in VmwareHandler.managedObjectCaches:
                VmwareHandler.managedObjectCaches[assetId] = dict()
        except Exception as e:
            raise e
