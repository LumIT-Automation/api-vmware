from typing import List, TYPE_CHECKING
from pyVmomi import vim

if TYPE_CHECKING:
    from vmware.models.VMware.HostSystem import HostSystem
from vmware.models.VMware.backend.Network import Network as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class Network(Backend):
    def __init__(self, assetId: int, moId: str, name: str = "", vlanId: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.vlanId = vlanId
        self.type: str
        if name:
            self.name = name
        else:
            self.name = self.oNetwork.name

        self.configuredHosts: List[HostSystem] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadConfiguredHostSystems(self) -> None:
        from vmware.models.VMware.HostSystem import HostSystem

        try:
            for h in self.oHostSystems():
                c = VmwareHelper.vmwareObjToDict(h)

                self.configuredHosts.append(
                    HostSystem(self.assetId, c["moId"])
                )
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
                network = Network(assetId, VmwareHelper.vmwareObjToDict(o)["moId"])
                networks.append(
                    Network.__cleanup("list", network.info(related))
                )

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
