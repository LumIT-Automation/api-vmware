from typing import List

from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network
from vmware.models.VMware.backend.HostSystem import HostSystem as Backend

from vmware.helpers.VMware.VmwareHelper import VmwareHelper


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
                        VmwareHelper.getInfo(d)["moId"]
                    )
                )
        except Exception as e:
            raise e



    def loadNetworks(self, specificMoId: str = "") -> None:
        try:
            pgList = self.oHostSystem.config.network.portgroup # standard port groups, basic info.
            for net in self.oNetworks(specificMoId):
                moId: str = ""
                name: str = ""
                vlanId: str = ""

                if hasattr(net, "config"):
                    # Distributed port group, first. The vmware DistributedVirtualPortgroup object type extends the Network type.
                    # Standard port group vlan id info should be taken from the host instead.
                    moId = net._GetMoId()
                    name = net.config.name
                    vlan = net.config.defaultPortConfig.vlan.vlanId
                    if isinstance(vlan, int):
                        vlanId = str(vlan)
                    elif isinstance(vlan, list):
                        # For a trunk port group the vlanId field is a list of vim.NumericRange data type.
                        try:
                            for idRange in vlan:
                                vlanId = str(idRange.start) + "-" + str(idRange.end)
                        except Exception:
                            pass
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



    def info(self, loadDatastores: bool = True, loadNetworks: bool = True, specificNetworkMoId: str = "") -> dict:
        ds = list()
        net = list()

        try:
            if loadDatastores:
                # Datastores' information.
                self.loadDatastores()
                for datastore in self.datastores:
                    ds.append(
                        HostSystem.__cleanup("info.datastore", datastore.info(False))
                    )

            if loadNetworks:
                # Networks' information.
                self.loadNetworks(specificNetworkMoId)
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
        except Exception as e:
            raise e



    def __contains__(self, objMoId):
        objType = VmwareHelper.getType(objMoId)

        if objType == "network":
            self.loadNetworks(objMoId)
            for network in self.networks:
                if network.moId == objMoId:
                    return True

        if objType == "datastore":
            self.loadDatastores()
            for datastore in self.datastores:
                if datastore.moId == objMoId:
                    return True

        return False



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, related: bool = False) -> List[dict]:
        hostsystems = list()

        try:
            for o in Backend.oHostSystems(assetId):
                hostsystem = HostSystem(assetId, VmwareHelper.getInfo(o)["moId"])
                hostsystems.append(
                    HostSystem.__cleanup("list", hostsystem.info(loadDatastores=related, loadNetworks=related))
                )

            return hostsystems
        except Exception as e:
            raise e



    @staticmethod
    def listQuick(assetId: int) -> List[dict]:
        hostsystems = list()

        try:
            for o in Backend.oHostSystems(assetId):
                hostsystem = VmwareHelper.getInfo(o)
                hostsystem["assetId"] = assetId
                hostsystems.append(hostsystem)

            return hostsystems
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        try:
            if oType == "info.datastore":
                if not o["attachedHosts"]:
                    del(o["attachedHosts"])

            if oType == "list":
                if not o["datastores"]:
                    del (o["datastores"])
                if not o["networks"]:
                    del (o["networks"])
        except Exception:
            pass

        return o
