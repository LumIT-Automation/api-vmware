from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler


class Datacenter(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oDatacenter = self.__oDatacenterLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oClusters(self) -> list:
        try:
            children = []
            for child in self.oDatacenter.hostFolder.childEntity:
                if isinstance(child, vim.ClusterComputeResource):
                    children.append(child)
            return children
        except Exception as e:
            raise e



    def oHosts(self) -> list:
        try:
            children = []
            for child in self.oDatacenter.hostFolder.childEntity:
                if isinstance(child, vim.ComputeResource) and not isinstance(child, vim.ClusterComputeResource):
                    children.append(child.host[0])
            return children
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def oDatacenters(assetId) -> list:
        try:
            return VmwareHandler().getObjects(assetId=assetId, vimType=vim.Datacenter)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oDatacenterLoad(self):
        try:
            return self.getObjects(assetId=self.assetId, vimType=vim.Datacenter, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=404, payload={"VMware": "Cannot load resource."})
