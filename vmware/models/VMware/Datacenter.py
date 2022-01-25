from typing import List

from pyVmomi import vim, vmodl

from vmware.models.VmwareContractor import VmwareContractor
from vmware.models.VMware.Cluster import Cluster

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log



class Datacenter(VmwareContractor):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId

        self.clusters: List[Cluster] = []

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        clusters = []
        try:
            computeResourcesList = self.listComputeResourcesObjects()
            # each element of computeResourcesList is a set containing a vmware ClusterComputeResource object.
            for c in computeResourcesList:
                clusters.append(VmwareHelper.vmwareObjToDict(c))

            return dict({
                "clusters": clusters,
            })

        except Exception as e:
            raise e



    def listComputeResourcesObjects(self) -> list:
        computeResources = []
        try:
            self.getVMwareObject()
            for child in self.oCluster.hostFolder.childEntity:
                if isinstance(child, vim.ComputeResource):
                    computeResources.append(child)
            return computeResources

        except Exception as e:
            raise e






    def getVMwareObject(self) -> None:
        try:
            self._getContainer(vim.Datacenter)

        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId, silent: bool = True) -> dict:
        datacenters = []
        try:
            dcObjList = Datacenter.listDatacentersObjects(assetId, silent)

            for dc in dcObjList:
                datacenters.append(VmwareHelper.vmwareObjToDict(dc))

            return dict({
                "items": datacenters
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter datacenter pyVmomi objects list.
    def listDatacentersObjects(assetId, silent: bool = True) -> list:
        try:
            vClient = VmwareContractor.connectToAssetAndGetContentStatic(assetId, silent)
            dcObjList = vClient.getAllObjs([vim.Datacenter])

            return dcObjList
        except Exception as e:
            raise e








    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            computeResourcesList = self.listComputeResourcesObjects()
            # each element of computeResourcesList is a set containing a vmware ClusterComputeResource object.
            for c in computeResourcesList:
                z = VmwareHelper.vmwareObjToDict(c)
                self.clusters.append(
                    Cluster(self.assetId, z["moId"])
                )
            Log.log(self.clusters, "_")
        except Exception as e:
            raise e
