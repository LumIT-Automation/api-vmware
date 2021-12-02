from pyVmomi import vim, vmodl

from vmware.models.VMware.Asset.Asset import Asset
from vmware.models.VMwareDjangoObj import VMwareDjangoObj

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.VMwareObj import VMwareObj
from vmware.helpers.Log import Log



class Datacenter(VMwareDjangoObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def listComputeResources(self) -> object:
        computeResources = []
        try:
            self.__getObject()
            dcObj = self.vmwareObj
            for child in dcObj.hostFolder.childEntity:
                if isinstance(child, vim.ComputeResource):
                    computeResources.append({child})
            return computeResources

        except Exception as e:
            raise e



    def info(self) -> dict:
        clusters = []
        try:
            computeResources = self.listComputeResources()
            # each element of computeResources is a set containing a vmware ClusterComputeResource object.
            for cr in computeResources:
                for c in cr:
                    clusters.append(VMwareObj.vmwareObjToDict(c))

            return dict({
                "items": clusters
            })

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = None) -> list:
        dcObjList = list()

        try:
            vClient = VMwareDjangoObj.connectToAssetStatic(assetId, silent)
            dcObjList = vClient.getAllObjs([vim.Datacenter])

            return dcObjList

        except Exception as e:
            raise e



    @staticmethod
    # Plain vCenter datacenters list.
    def listData(assetId, silent: bool = None) -> dict:
        datacenters = []
        try:
            dcObjList = Datacenter.list(assetId, silent)

            for dc in dcObjList:
                datacenters.append(VMwareObj.vmwareObjToDict(dc))

            return dict({
                "items": datacenters
            })

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getObject(self, silent: bool = None) -> None:
        try:
            self._getObject(vim.Datacenter, silent)

        except Exception as e:
            raise e

