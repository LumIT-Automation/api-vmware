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
            for n in self.oNetworks():
                self.networks.append(
                    Network(
                        self.assetId,
                        VmwareHelper.vmwareObjToDict(n)["moId"]
                    )
                )
        except Exception as e:
            raise e



    # OLD CODE: this one get the vlan id also.
    #def loadNetworks(self) -> None:
    #    try:
    #        pgList = self.oHostSystem.config.network.portgroup
    #        for n in self.oNetworks():
    #            net = VmwareHelper.vmwareObjToDict(n)

    #            if hasattr(n,
    #                      'config'):  # distributed port group. Standard switch vlan id should be taken from the host.
    #                net["vlanId"] = n.config.defaultPortConfig.vlan.vlanId
    #           else:
    #                for pg in pgList:
    #                    if pg.spec.name == net[
    #                        "name"]:  # Standard switch. This works because standard switch names cannot be duplicated.
    #                        net["vlanId"] = pg.spec.vlanId
    #            self.networks.append(net)

    #           self.networks.append(
    #                Network(
    #                    self.assetId,
    #                    VmwareHelper.vmwareObjToDict(n)["moId"]
    #                )
    #            )
    #    except Exception as e:
    #        raise e



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
            net.append(
                HostSystem.__cleanup(
                    "network",
                    network.info(False)
                )
            )

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
