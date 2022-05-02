from typing import List, Any

from pyVmomi import vim
from cachetools import TTLCache

from django.conf import settings

from vmware.models.VMware.Asset.Asset import Asset

from vmware.helpers.VMware.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class VmwareHandler:
    contents = dict() # share content amongst all instances: do not re-fetch it during a "session" [!! in daemon mode: until an apache restart !!].
    managedObjectCaches = dict()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



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

                                # Save content into managedObjectCaches[assetId][moId] "cache" with the ttl timeout defined:
                                # VmwareHandler.contents[assetId] object's token expires after some time (==timeout) (and fires a vim.fault.NotAuthenticated exception).
                                # We can handle the token expiration via the vim.fault.NotAuthenticated catching below only when object is not in the cache.
                                # On the contrary ('cause we serve the cached object anyway), we must set a caching-timeout when saving managedObjectCaches[assetId][moId]
                                # (after the timeout, managedObjectCaches[assetId][moId] becomes None).
                                VmwareHandler.managedObjectCaches[assetId][moId] = managedObject_ref
                                break
                else:
                    # Return complete list.
                    c = VmwareHandler.contents[assetId].viewManager.CreateContainerView(VmwareHandler.contents[assetId].rootFolder, [vimType], True)
                    for managedObject_ref in c.view:
                        obj.append(managedObject_ref)
            else:
                raise CustomException(status=400, payload={"VMware": "cannot fetch VMware objects."})
        except vim.fault.NotAuthenticated: # when token expires.
            self.__fetchContent(assetId)
            obj = self.getObjects(assetId, vimType, moId)
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
            connection = VmwareSupplicant(Asset(assetId)).connect()

            Log.actionLog("Fetch VMware content from connection.")
            VmwareHandler.contents[assetId] = connection.RetrieveContent()

            if assetId not in VmwareHandler.managedObjectCaches:
                VmwareHandler.managedObjectCaches[assetId] = TTLCache(maxsize=100, ttl=settings.VMWARE_CONTENT_CACHE_TIMEOUT)
        except Exception as e:
            raise e
