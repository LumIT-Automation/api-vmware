from typing import List

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log

from vmware.models.VMware.Cluster import Cluster

from vmware.models.VMware.backend.Datacenter import Datacenter as Backend


class Datacenter(Backend):
    def __init__(self, assetId: int, moId: str, name: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = name

        self.clusters: List[Cluster] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadClusters(self) -> None:
        try:
            for c in self.oClusters():
                self.clusters.append(
                    Cluster(
                        self.assetId,
                        VmwareHelper.vmwareObjToDict(c)["moId"],
                        VmwareHelper.vmwareObjToDict(c)["name"],
                    )
                )
        except Exception as e:
            raise e



    def loadRelated(self):
        self.loadClusters()



    def info(self):
        lc = list()
        self.loadRelated()

        for cluster in self.clusters:
            lc.append(cluster.info(False))

        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "name": self.oDatacenter.name,
            "clusters": lc
        }



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId) -> List[dict]:
        datacenters = list()

        try:
            for d in Backend.oDatacenters(assetId):
                data = {"assetId": assetId}
                data.update(VmwareHelper.vmwareObjToDict(d))

                datacenters.append(data)

            return datacenters
        except Exception as e:
            raise e
