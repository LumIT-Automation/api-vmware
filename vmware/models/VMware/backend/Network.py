from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log

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



    def listVmsIps(self, othersVMsIp: bool = False) -> list:
        ipList = list()

        try:
            oVmList = self.listAttachedVMs()

            for vm in oVmList:
                vmIps = list()
                vmInfo = {
                    "moId": vm._GetMoId(),
                    "name": vm.name,
                    "ipList": []
                }
                if hasattr(vm, "guest"):
                    if hasattr(vm.guest, "net"):
                        for nic in vm.guest.net:
                            nicInfo = {
                                "pgName": "",
                                "ipAddress": []
                            }
                            if hasattr(nic, "network"):
                                if nic.network:
                                    nicInfo["pgName"]= nic.network
                                else:
                                    nicInfo["pgName"] = "loopback nic"

                            if hasattr(nic, "ipConfig"):
                                if hasattr(nic.ipConfig, "ipAddress"):
                                    for ipData in nic.ipConfig.ipAddress:
                                        nicInfo["ipAddress"].append(ipData.ipAddress)
                            vmIps.append(nicInfo)

                vmInfo["ipList"] = vmIps
                ipList.append(vmInfo)

            return ipList
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
