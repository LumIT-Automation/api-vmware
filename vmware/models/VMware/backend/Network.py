from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.vmware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log


class Network(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

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



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def oNetworks(assetId) -> list:
        try:
            return VmwareHandler(assetId).getObjects(vimType=vim.Network)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oNetworkLoad(self):
        try:
            return self.getObjects(vimType=vim.Network, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=400, payload={"VMware": "cannot load resource."})