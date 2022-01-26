from typing import List

from vmware.helpers.vmware.VmwareHelper import VmwareHelper

from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.backend.Cluster import Cluster as Backend


class Cluster(Backend):
    def __init__(self, assetId: int, moId: str, name: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = name

        self.hosts: List[dict] = []
        self.datastores: List[Datastore] = []
        self.networks: List[dict] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadHosts(self) -> None:
        try:
            for h in self.oHosts():
                self.hosts.append(VmwareHelper.vmwareObjToDict(h))
        except Exception as e:
            raise e



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
                self.networks.append(VmwareHelper.vmwareObjToDict(n))
        except Exception as e:
            raise e



    def loadRelated(self):
        self.loadHosts()
        self.loadDatastores()
        self.loadNetworks()



    def info(self, related: bool = True) -> dict:
        ds = list()
        if related:
            self.loadRelated()

        for datastore in self.datastores:
            ds.append(datastore.info())

        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "name": self.name,
            "hosts": self.hosts,
            "datastores": ds,
            "networks": self.networks,
        }



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter clusters list.
    def list(assetId) -> List[dict]:
        clusters = list()

        try:
            for el in Backend.oClusters(assetId):
                clusters.append(VmwareHelper.vmwareObjToDict(el))

            return clusters
        except Exception as e:
            raise e
