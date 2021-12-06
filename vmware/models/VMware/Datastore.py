from pyVmomi import vim, vmodl

from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VMwareObj import VMwareObj
from vmware.helpers.Log import Log



class Datastore(VMwareDjangoObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        attachedHosts = []
        datastoreInfo = []
        try:
            attachedHostsObjs = self.listAttachedHostsObjects()
            for h in attachedHostsObjs:
                attachedHosts.append(VMwareObj.vmwareObjToDict(h))

            datastoreInfo = self.getDatastoreInfo()

            return dict({
                "attachedHosts": attachedHosts,
                "datastoreInfo": datastoreInfo
            })

        except Exception as e:
            raise e



    def getDatastoreInfo(self) -> dict:
        info = dict()
        try:
            dsInfo = self.getDatastoreInfoObject()
            info["name"] = dsInfo.name
            info["url"] = dsInfo.url
            info["freeSpace"] = dsInfo.freeSpace
            info["maxFileSize"] = dsInfo.maxFileSize
            info["maxVirtualDiskCapacity"] = dsInfo.maxVirtualDiskCapacity

            if hasattr(dsInfo, 'nas'):
                info["type"] = dsInfo.nas.type
                info["capacity"] = dsInfo.nas.capacity
            elif hasattr(dsInfo, 'vmfs'):
                info["type"] = dsInfo.vmfs.type
                info["capacity"] = dsInfo.vmfs.capacity
                info["ssd"] = dsInfo.vmfs.ssd
                info["majorVersion"] = dsInfo.vmfs.majorVersion
                info["local"] = dsInfo.vmfs.local

            return info

        except Exception as e:
            raise e



    def getDatastoreInfoObject(self) -> object:
        try:
            self.__getVMwareObject()
            return self.vmwareObj.info

        except Exception as e:
            raise e



    def listAttachedHostsObjects(self) -> list:
        hosts = []
        try:
            self.__getVMwareObject()
            hostMounts = self.vmwareObj.host
            for h in hostMounts:
                if h.mountInfo.mounted is True and h.mountInfo.accessible is True and h.mountInfo.accessMode == "readWrite":
                    hosts.append(h.key)

            return hosts

        except Exception as e:
            raise e

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datastores list.
    def list(assetId, silent: bool = None) -> dict:
        datastores = []
        try:
            dsObjList = Datastore.listDatastoresObjects(assetId, silent)

            for ds in dsObjList:
                datastores.append(VMwareObj.vmwareObjToDict(ds))

            return dict({
                "items": datastores
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter datastores pyVmomi objects list.
    def listDatastoresObjects(assetId, silent: bool = None) -> list:
        dsObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetStatic(assetId, silent)
            dsObjList = vClient.getAllObjs([vim.Datastore])

            return dsObjList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getVMwareObject(self, refresh: bool = False, silent: bool = None) -> None:
        try:
            self._getVMwareObject(vim.Datastore, refresh, silent)

        except Exception as e:
            raise e

