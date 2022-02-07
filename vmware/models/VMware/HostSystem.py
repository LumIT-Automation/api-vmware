from typing import List

from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network
from vmware.models.VMware.backend.HostSystem import HostSystem as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class HostSystem(Backend):
    def __init__(self, assetId: int, moId: str, name: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = name

        self.networks: List[Network] = []
        self.datastores: List[Datastore] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadDatastores(self) -> None:
        try:
            for d in self.oDatastores():
                self.datastores.append(
                    Datastore(
                        self.assetId,
                        VmwareHelper.vmwareObjToDict(d)["moId"]
                    )
                )
        except Exception as e:
            raise e



    def loadNetworks(self) -> None:
        try:
            pgList = self.oHostSystem.config.network.portgroup # Get Standard port groups basic info.
            for net in self.oNetworks():
                moId: str = ""
                name: str = ""
                vlanId: int = None
                # Distributed port group first. The vmware DistributedVirtualPortgroup object type extends the Network type.
                # Standard port group vlan id info should be taken from the host instead.
                if hasattr(net, 'config'):
                    moId = net._GetMoId()
                    name = net.config.name
                    if isinstance(net.config.defaultPortConfig.vlan.vlanId, int):
                        vlanId = net.config.defaultPortConfig.vlan.vlanId
                else:
                    # Standard port group.
                    for pg in pgList:
                        if pg.spec.name == net.name:
                            moId = net._GetMoId()
                            name = net.name
                            vlanId = pg.spec.vlanId

                self.networks.append(
                    Network(self.assetId, moId, name, vlanId)
                )

        except Exception as e:
            raise e



    def info(self, related: bool = True) -> dict:
        ds = list()
        net = list()

        if related:
            self.loadDatastores()
            self.loadNetworks()

        # Datastores' information.
        for datastore in self.datastores:
            ds.append(
                HostSystem.__cleanup(
                    "datastore",
                    datastore.info(False)
                )
            )

        # Networks' information.
        for network in self.networks:
            net.append({
                "assetId": network.assetId,
                "moId": network.moId,
                "name": network.name,
                "vlanId": network.vlanId
            })

        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "name": self.oHostSystem.name,

            "datastores": ds,
            "networks": net
        }



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId) -> List[dict]:
        hostsystems = list()

        try:
            for h in Backend.oHostSystems(assetId):
                data = {"assetId": assetId}
                data.update(VmwareHelper.vmwareObjToDict(h))

                hostsystems.append(data)

            return hostsystems
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        if oType == "datastore":
            if not o["attachedHosts"]:
                del(o["attachedHosts"])

        if oType == "network":
            if not o["configuredHosts"]:
                del (o["configuredHosts"])

        return o
