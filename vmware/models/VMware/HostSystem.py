from pyVmomi import vim
from typing import List

from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network
from vmware.models.VMware.backend.HostSystem import HostSystem as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper


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



    def loadRelated(self):
        self.loadDatastores()
        self.loadNetworks()



    def info(self, related: bool = True) -> dict:
        data = {
            "assetId": self.assetId,
            "moId": self.moId,
            "name": self.oHostSystem.name,
        }

        if related:
            self.loadRelated()
            ds = list()
            net = list()

            for d in self.datastores:
                dsData = {
                    "moId": d.moId,
                    "name": ""
                }
                ds.append(dsData)
            data["datastores"] = ds

            for n in self.networks:
                netData = {
                    "moId": n.moId,
                    "name": "",
                    "vlanId": ""
                }
                net.append(netData)
            data["networks"] = net

        return data



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

