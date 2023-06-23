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



    def listVmsIps(self) -> list:
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



    def getVlanIds(self) -> set:
        vlanId = set()
        try:
            # Distributed port group, first. The vmware DistributedVirtualPortgroup object type extends the Network type.
            if hasattr(self.oNetwork, "config"):
                vlan = self.oNetwork.config.defaultPortConfig.vlan.vlanId
                if isinstance(vlan, int):
                    vlanId.add(str(vlan))
                elif isinstance(vlan, list):
                    # For a trunk port group the vlanId field is a list of vim.NumericRange data type, with the properties "start and "end" for a vlan ids range.
                    try:
                        for idRange in vlan:
                            for id in range(idRange.start, idRange.end+1):
                                vlanId.add(str(id))
                    except Exception:
                        pass

            # Standard port group vlan id info should be taken from the host instead.
            else:
                if self.oNetwork.host:
                    host = self.oNetwork.host[0] # Get the vlan info from the first host of the list.
                    for pg in host.config.network.portgroup: # standard port groups, basic info.
                        if pg.spec.name == self.oNetwork.name:
                            vlanId.add(str(pg.spec.vlanId))
                            break
            return vlanId
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
            raise CustomException(status=404, payload={"VMware": "Cannot load resource."})
