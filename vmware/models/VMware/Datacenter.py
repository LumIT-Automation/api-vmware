from typing import List

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log

from vmware.models.VMware.backend.Datacenter import Datacenter as Backend


class Datacenter(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId

        self.clusters: List[dict] = []




    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadClusters(self) -> None:
        try:
            for c in self.oClusters():
                self.clusters.append(VmwareHelper.vmwareObjToDict(c))
        except Exception as e:
            raise e



    def loadRelated(self):
        self.loadClusters()



    def info(self):
        self.loadRelated()

        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "clusters": self.clusters
        }



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId) -> list:
        datacenters = list()

        try:
            for d in Backend.oDatacenters(assetId):
                datacenters.append(VmwareHelper.vmwareObjToDict(d))

            return datacenters
        except Exception as e:
            raise e