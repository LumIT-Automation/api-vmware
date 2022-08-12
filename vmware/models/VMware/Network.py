from typing import List, TYPE_CHECKING
from pyVmomi import vim

if TYPE_CHECKING:
    from vmware.models.VMware.HostSystem import HostSystem
from vmware.models.VMware.backend.Network import Network as Backend

from vmware.helpers.VMware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log

class Network(Backend):
    def __init__(self, assetId: int, moId: str, name: str = "", vlanId: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = name
        self.vlanId = vlanId
        self.type: str

        self.configuredHosts: List[HostSystem] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadConfiguredHostSystems(self) -> None:
        from vmware.models.VMware.HostSystem import HostSystem

        try:
            for h in self.oHostSystems():
                c = VmwareHelper.getInfo(h)

                self.configuredHosts.append(
                    HostSystem(self.assetId, c["moId"])
                )
        except Exception as e:
            raise e



    def listVmsIps(self) -> list:
        from vmware.models.VMware.VirtualMachine import VirtualMachine
        ipList = list()

        try:
            oVmList = Backend.listAttachedVMs(self)
            self.name = self.oNetwork.summary.name
            for v in oVmList:
                vm = VmwareHelper.getInfo(v)
                virtualmachine = VirtualMachine(self.assetId, vm["moId"])
                vmGuestInfo = virtualmachine.guestInfo()
                if "network" in vmGuestInfo and self.name in vmGuestInfo["network"] and vmGuestInfo["network"][self.name]: # Get only the info about this port group if the vm have more than one network card.
                    ipList.append(
                        {
                            "moId": vm["moId"],
                            "name": vm["name"],
                            "ipList": vmGuestInfo["network"][self.name]
                        }

                    )

            return ipList
        except Exception as e:
            raise e



    def getVlanIds(self) -> set:
        vlanId = set()
        try:
            self.loadConfiguredHostSystems()
            for chost in self.configuredHosts:
                host = chost.info(loadDatastores=False, specificNetworkMoId=self.moId)
                if "networks" in host:
                    for net in host["networks"]:
                        if "vlanId" in net: # This value is an integer for standard port groups, a string for distributed port groups.
                            # The string can contain a single number, a range, a list. Eg: 2, 11, 111-115, 5
                            for id in str(net["vlanId"]).split(', '):
                                if "-" in id: # Range of vlan ids (eg: 111-115)
                                    idRange = id.split('-')
                                    for i in range(int(idRange[0]), int(idRange[-1])+1, 1):
                                        vlanId.add(str(i))
                                else:
                                    vlanId.add(id) # Single vlan id.

            return vlanId
        except Exception as e:
            raise e



    def getNetWithSameVlanIds(self) -> List[object]:
        networks = list()

        try:
            vlanIds = self.getVlanIds() # Vlan ids of this network.
            for o in Backend.oNetworks(self.assetId):
                network = Network(self.assetId, VmwareHelper.getInfo(o)["moId"])
                netVlanIds = network.getVlanIds() # Vlan ids of another network.
                for netVlanId in netVlanIds:
                    for vlanId in vlanIds:
                        if netVlanId == str(vlanId):
                            networks.append(network)

            return networks
        except Exception as e:
            raise e



    def findVMsWithThisIpAddress(self, ipAddress: str):
        vms = list()

        try:
            nets = self.getNetWithSameVlanIds()

            for net in nets:
                for vm in net.listVmsIps():
                    for ip in vm["ipList"]:
                        if ip == ipAddress:
                            vms.append({
                                "moId": vm["moId"],
                                "name": vm["name"]
                            })

            return vms
        except Exception as e:
            raise e




    def info(self, related: bool = True) -> dict:
        hosts = list()
        portGroupType = ""

        try:
            if isinstance(self.oNetwork, vim.Network):
                portGroupType = "standard"
            if isinstance(self.oNetwork, vim.dvs.DistributedVirtualPortgroup):
                portGroupType = "distributed"

            if related:
                # Configured hosts' information.
                # Need to load hosts' data in order to fetch related network information for each host.
                self.loadConfiguredHostSystems()
                for chost in self.configuredHosts:
                    hosts.append(
                        Network.__cleanup("info", chost.info(loadDatastores=False, specificNetworkMoId=self.moId))
                    )

            return {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": self.oNetwork.summary.name,
                "accessible": self.oNetwork.summary.accessible,
                "type": portGroupType,

                "configuredHosts": hosts
            }
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, related: bool = False) -> List[dict]:
        networks = list()

        try:
            for o in Backend.oNetworks(assetId):
                network = Network(assetId, VmwareHelper.getInfo(o)["moId"])
                networks.append(
                    Network.__cleanup("list", network.info(related))
                )

            return networks
        except Exception as e:
            raise e



    @staticmethod
    def listQuick(assetId: int) -> List[dict]:
        networks = list()

        try:
            for o in Backend.oNetworks(assetId):
                network = VmwareHelper.getInfo(o)
                network["assetId"] = assetId
                networks.append(network)

            return networks
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        if oType == "info":
            if not o["datastores"]:
                del (o["datastores"])

        if oType == "list":
            if not o["configuredHosts"]:
                del (o["configuredHosts"])

        return o
