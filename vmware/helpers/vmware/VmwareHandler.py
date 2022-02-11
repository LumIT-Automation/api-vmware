from typing import List, Any

from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.vmware.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class VmwareHandler:
    content = None # share content amongst all instances: do not re-fetch it during a "session".
    managedObjectCache = dict()

    def __init__(self, assetId: int, moId: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId # VMware Managed Object Id.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    # Get VMware objects of type vimType.
    # vimTypes: vim.VirtualMachine, vim.Folder, vim.Datacenter, vim.VirtualApp, vim.ComputeResource, vim.Network, vim.Datastore.
    def getObjects(self, vimType: str, moId: str = "") -> List[Any]:
        obj = []

        try:
            if not VmwareHandler.content:
                self.__fetchContent()

            if VmwareHandler.content:
                if moId:
                    # Return one moId (need an exact search here).
                    if moId in VmwareHandler.managedObjectCache:
                        # Search within the class "cache", first.
                        obj.append(VmwareHandler.managedObjectCache[moId])
                    else:
                        c = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vimType], True)
                        for managedObject_ref in c.view:
                            if managedObject_ref._GetMoId() == moId:
                                obj.append(managedObject_ref)

                                VmwareHandler.managedObjectCache[moId] = managedObject_ref # put in "cache".
                                break
                else:
                    # Return complete list.
                    c = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vimType], True)
                    for managedObject_ref in c.view:
                        obj.append(managedObject_ref)
            else:
                raise CustomException(status=400, payload={"VMware": "cannot fetch VMware objects."})
        except Exception as e:
            raise e

        return obj



    ####################################################################################################################
    # Protected methods
    ####################################################################################################################

    def _getSubContent(self, prop: str) -> object:
        try:
            if not VmwareHandler.content:
                self.__fetchContent()

            return getattr(VmwareHandler.content, prop)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __fetchContent(self) -> None:
        try:
            supplicant = VmwareSupplicant(Asset(self.assetId).connectionData)
            connection = supplicant.connect()

            Log.actionLog("Fetch VMware content.")
            VmwareHandler.content = connection.RetrieveContent()
        except Exception as e:
            raise e
