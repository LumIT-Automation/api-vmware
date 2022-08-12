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



    def listUsedIps(self) -> list:
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



    def getVlanIds(self):
        vlanId = set()
        try:
            self.loadConfiguredHostSystems()
            for chost in self.configuredHosts:
                host = chost.info(loadDatastores=False, specificNetworkMoId=self.moId)
                if "networks" in host:
                    for net in host["networks"]:
                        if "vlanId" in net:
                            vlanId.add(net["vlanId"])

            return vlanId
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
