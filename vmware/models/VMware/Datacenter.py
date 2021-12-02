from pyVmomi import vim, vmodl

from vmware.models.VMware.Asset.Asset import Asset
from vmware.models.VMwareObj import VMwareObj

from vmware.helpers.VmwareSupplicant import VmwareSupplicant
from vmware.helpers.Log import Log



class Datacenter(VMwareObj):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def listComputeResources(self):
        dc = self.__getObject()
        clusters = []
        try:
            for cl in dc.hostFolder.childEntity:
                if isinstance(cl, vim.ComputeResource):
                    clusters.append({cl})

            return clusters


        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = None) -> dict:
        datacenters = list()

        try:
            vClient = VMwareObj.connectToAssetStatic(assetId, silent)

            dcList = vClient.getAllObjs([vim.Datacenter])
            for dc in dcList:
                datacenters.append({
                    "moId": dc._moId,
                    "name": dc.name
                })

            return dict({
                "items": datacenters
            })

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getObject(self, silent: bool = None) -> object:
        obj = None
        try:
            obj = self._getObject(vim.Datacenter, silent)
            return obj

        except Exception as e:
            raise e

