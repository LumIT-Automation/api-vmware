from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler


class Cluster(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    def oClusters(assetId) -> list:
        try:
            return VmwareHandler().getObjects(assetId=assetId, vimType=vim.ClusterComputeResource)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oClusterLoad(self):
        try:
            return self.getObjects(assetId=self.assetId, vimType=vim.ClusterComputeResource, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=404, payload={"VMware": "cannot load resource."})
