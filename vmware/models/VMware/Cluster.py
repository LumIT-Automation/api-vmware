from typing import List
from pyVmomi import vim, vmodl

from vmware.models.VmwareContractor import VmwareContractor

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log

from vmware.models.VMware.backend.Cluster import Cluster as Backend


class Cluster(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId

        self.hosts: List[dict] = []
        self.datastores: List[dict] = []
        self.networks: List[dict] = []

        self.__load()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    def info(self):
        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "hosts": self.hosts,
            "datastores": self.datastores,
            "networks": self.networks,
        }



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter clusters list.
    def list(assetId, silent: bool = True) -> dict:
        clusters = list()
        try:
            clustersObjList = Cluster.listClustersObjects(assetId, silent)
            for cl in clustersObjList:
                clusters.append(VmwareHelper.vmwareObjToDict(cl))

            return dict({
                "items": clusters
            })

        except Exception as e:
            raise e



    @staticmethod
    # vCenter cluster pyVmomi objects list.
    def listClustersObjects(assetId, silent: bool = True) -> list:
        clustersObjList = list()

        try:
            vClient = VmwareContractor.connectToAssetAndGetContentStatic(assetId, silent)
            clList = vClient.getAllObjs([vim.ComputeResource])

            for cl in clList:
                clustersObjList.append(cl)

            return clustersObjList

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            for h in self.oHosts():
                self.hosts.append(VmwareHelper.vmwareObjToDict(h))

            for d in self.oDatastores():
                self.datastores.append(VmwareHelper.vmwareObjToDict(d))

            for n in self.oNetworks():
                self.networks.append(VmwareHelper.vmwareObjToDict(n))
        except Exception as e:
            raise e
