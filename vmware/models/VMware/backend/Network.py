from pyVmomi import vim

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



    def oInfoLoad(self) -> object:
        try:
            netInfo = dict()

            netSummary = self.oNetwork.summary
            netInfo["name"] = netSummary.name
            netInfo["accessible"] = netSummary.accessible

            if hasattr(self.oNetwork, 'config'): # distributed port group. Standard switch vlan id should be taken from the host.
                netInfo["vlanId"] = self.oNetwork.config.defaultPortConfig.vlan.vlanId

            return netInfo
        except Exception as e:
            raise e

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # vCenter network pyVmomi objects list.
    def oNetworks(assetId) -> list:
        oNetworkList = list()

        try:
            nlList = VmwareHandler(assetId).getObjects(vimType=vim.Network)
            for n in nlList:
                oNetworkList.append(n)

            return oNetworkList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oNetworkLoad(self):
        for k, v in self.getObjects(vimType=vim.Network).items():
            if k._GetMoId() == self.moId:
                return k
