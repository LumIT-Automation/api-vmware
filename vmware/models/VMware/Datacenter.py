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
        # Load VMware cluster objects.
        try:
            for c in self.oClusters():
                cl = VmwareHelper.vmwareObjToDict(c)

                self.clusters.append(
                    Cluster(self.assetId, cl["moId"], cl["name"])
                )
        except Exception as e:
            raise e



    def info(self):
        lc = list()
        self.loadClusters()

        for cluster in self.clusters:
            c = cluster.info(False)

            # Remove some related objects' information if not loaded.
            if not c["hosts"]:
                del(c["hosts"])

            if not c["datastores"]:
                del(c["datastores"])

            if not c["networks"]:
                del(c["networks"])

            lc.append(c)

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

                # Add clusters information.
                dc = Datacenter(data["assetId"], data["moId"])
                data.update({"clusters": dc.info()["clusters"]})

                datacenters.append(data)

            return datacenters
        except Exception as e:
            raise e
