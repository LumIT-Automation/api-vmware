from typing import List

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log

from vmware.models.VMware.backend.Cluster import Cluster as Backend


class Cluster(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId

        self.hosts: List[dict] = []
        self.datastores: List[dict] = []
        self.networks: List[dict] = []

        self.__load()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    def info(self):
        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "hosts": self.hosts,
            "datastores": self.datastores,
            "networks": self.networks,
        }



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter clusters list.
    def list(assetId) -> list:
        clusters = list()

        try:
            for el in Backend.oClusters(assetId):
                clusters.append(VmwareHelper.vmwareObjToDict(el))

            return clusters
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            for h in self.oHosts():
                self.hosts.append(VmwareHelper.vmwareObjToDict(h))

            for d in self.oDatastores():
                self.datastores.append(VmwareHelper.vmwareObjToDict(d))

            for n in self.oNetworks():
                self.networks.append(VmwareHelper.vmwareObjToDict(n))
        except Exception as e:
            raise e
