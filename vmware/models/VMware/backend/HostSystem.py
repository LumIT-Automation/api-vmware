from pyVmomi import vim

from vmware.helpers.vmware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log


class HostSystem(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oHostSystem = self.__oHostSystemLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oDatastores(self) -> list:
        try:
            return self.oHostSystem.datastore
        except Exception as e:
            raise e



    def oNetworks(self, networkMoId: str = "") -> list:
        oNetwork = []

        try:
            networks = self.oHostSystem.network
            if networkMoId:
                for net in networks:
                    if networkMoId == net._GetMoId():
                        oNetwork.append(net)
                        break
            else:
                oNetwork = networks

            return oNetwork
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # vCenter hostsystem pyVmomi objects list.
    def oHostSystems(assetId) -> list:
        oHostSystemList = list()

        try:
            hList = VmwareHandler(assetId).getObjects(vimType=vim.HostSystem)
            for hs in hList:
                if not hasattr(hs, 'host'): # Standalone host.
                    oHostSystemList.append(hs)
                else:
                    for h in hs.host:
                        oHostSystemList.append(h) # In cluster host.
            return oHostSystemList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oHostSystemLoad(self):
        return self.getObjects(vimType=vim.HostSystem, moId=self.moId)[0]
