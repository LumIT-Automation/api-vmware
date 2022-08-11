from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler


class Network(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oNetwork = self.__oNetworkLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oHostSystems(self) -> list:
        try:
            return self.oNetwork.host
        except Exception as e:
            raise e



    def listAttachedVMs(self):
        try:
            return self.oNetwork.vm
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def oNetworks(assetId) -> list:
        try:
            return VmwareHandler().getObjects(assetId=assetId, vimType=vim.Network)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oNetworkLoad(self):
        try:
            return self.getObjects(assetId=self.assetId, vimType=vim.Network, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=404, payload={"VMware": "cannot load resource."})
