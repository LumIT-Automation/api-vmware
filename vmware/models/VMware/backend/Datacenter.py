from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.vmware.VmwareHandler import VmwareHandler


class Datacenter(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

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
                if isinstance(child, vim.HostSystem):
                    children.append(child)
                elif isinstance(child, vim.ClusterComputeResource):
                    children.extend(child.host)
            return children
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def oDatacenters(assetId) -> list:
        try:
            return VmwareHandler(assetId).getObjects(vimType=vim.Datacenter)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oDatacenterLoad(self):
        try:
            return self.getObjects(vimType=vim.Datacenter, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=400, payload={"VMware": "cannot load resource."})
