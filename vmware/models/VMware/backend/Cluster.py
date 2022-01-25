from typing import List
from pyVmomi import vim, vmodl

from vmware.models.VmwareContractor import VmwareContractor

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class Cluster(VmwareContractor):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.client = None

        self._getContract(vim.ComputeResource)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oHosts(self) -> list:
        try:
            return self.client.host
        except Exception as e:
            raise e



    def oDatastores(self) -> list:
        try:
            return self.client.datastore
        except Exception as e:
            raise e



    def oNetworks(self) -> list:
        try:
            return self.client.network
        except Exception as e:
            raise e



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


