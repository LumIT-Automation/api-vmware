from pyVmomi import vim
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

        self.networks: List[dict] = []
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
            pgList = self.oHostSystem.config.network.portgroup
            for n in self.oNetworks():
                net = VmwareHelper.vmwareObjToDict(n)

                if hasattr(n,'config'):  # distributed port group. Standard switch vlan id should be taken from the host.
                    Log.log('ggggg')
                    net["vlanId"] = n.config.defaultPortConfig.vlan.vlanId
                else:
                    for pg in pgList:
                        if pg.spec.name == net["name"]: # Standard switch. This works because standard switch names cannot be duplicated.
                            net["vlanId"] = pg.spec.vlanId
                self.networks.append(net)

        except Exception as e:
            raise e



    def loadRelated(self):
        self.loadDatastores()
        self.loadNetworks()



    def info(self, related: bool = True) -> dict:
        ds = list()
        if related:
            self.loadRelated()

        for datastore in self.datastores:
            d = datastore.info(False)
            if not d["attachedHosts"]:
                del(d["attachedHosts"])

            # List only multipleHostAccess: true.
            if d["multipleHostAccess"]:
                ds.append(d)

        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "name": self.oHostSystem.name,
            "datastores": ds,
            "networks": self.networks
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

