from pyVmomi import vim

from vmware.helpers.vmware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log


class Cluster(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oCluster = self.__oClusterLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oHosts(self) -> list:
        try:
            return self.oCluster.host
        except Exception as e:
            raise e



    def oDatastores(self) -> list:
        try:
            return self.oCluster.datastore
        except Exception as e:
            raise e



    def oNetworks(self) -> list:
        try:
            return self.oCluster.network
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # vCenter cluster pyVmomi objects list.
    def oClusters(assetId) -> list:
        oClusterList = list()

        try:
            clList = VmwareHandler(assetId).getObjects(vimType=vim.ClusterComputeResource)
            for cl in clList:
                oClusterList.append(cl)

            return oClusterList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oClusterLoad(self):
        o = self.getObjects(vimType=vim.ClusterComputeResource)

        for k, v in o.items():
            if k._GetMoId() == self.moId:
                return k
