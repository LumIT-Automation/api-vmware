from typing import List, TYPE_CHECKING
from pyVmomi import vim

if TYPE_CHECKING:
    from vmware.models.VMware.HostSystem import HostSystem
from vmware.models.VMware.backend.Network import Network as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class Network(Backend):
    def __init__(self, assetId: int, moId: str, name: str = "", vlanId: int = None, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = name
        self.vlanId = vlanId

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
                    Network.__info(
                        chost.info(loadDatastores=False, specificNetworkMoId=self.moId),
                        self.moId
                    )
                )

        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "name": self.oNetwork.summary.name,
            "accessible": self.oNetwork.summary.accessible,
            "type": portGroupType,

            "configuredHosts": hosts
        }



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId) -> List[dict]:
        networks = list()

        try:
            for n in Backend.oNetworks(assetId):
                data = {"assetId": assetId}
                data.update(VmwareHelper.vmwareObjToDict(n))
                networks.append(data)

            return networks
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __info(o: dict, moId: str):
        info = {
            "assetId": o["assetId"],
            "moId": o["moId"],
            "name": o["name"]
        }

        # Get port group information from each host. This is the right way for standard port group,
        # but works for distributed port group also.
        for n in o["networks"]:  # Data from HostSystem.info() method.
            # The vlanId field is an integer for if the port group is configured with an access vlan id.
            # For a trunk port group the vlanId field is a list of vim.NumericRange data type.
            if n["moId"] == moId and 'vlanId' in n:
                if type(n["vlanId"]) == int:
                    info["vlanId"] = str(n["vlanId"])
                elif isinstance(n["vlanId"], list):
                    # Trunk network.
                    try:
                        for idRange in n["vlanId"]:
                            info["vlanId"] = str(idRange.start) + "-" + str(idRange.end)
                    except Exception:
                        pass

        return o
