from typing import List

from vmware.models.VMware.Cluster import Cluster
from vmware.models.VMware.backend.Datacenter import Datacenter as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper


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
                cl = VmwareHelper.vmwareObjToDict(c)

                self.clusters.append(
                    Cluster(self.assetId, cl["moId"])
                )
        except Exception as e:
            raise e



    def info(self):
        lc = list()

        try:
            self.loadClusters()

            for cluster in self.clusters:
                lc.append(
                    Datacenter.__cleanup(
                        cluster.info(False)
                    )
                )

            return {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": self.oDatacenter.name,

                "clusters": lc
            }
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int) -> List[dict]:
        datacenters = list()

        try:
            for o in Backend.oDatacenters(assetId):
                datacenter = Datacenter(assetId, VmwareHelper.vmwareObjToDict(o)["moId"])
                datacenters.append(datacenter.info())

            return datacenters
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(o: dict):
        # Remove some related objects' information, if not loaded.
        if not o["hosts"]:
            del (o["hosts"])

        if not o["datastores"]:
            del (o["datastores"])

        if not o["networks"]:
            del (o["networks"])

        return o
