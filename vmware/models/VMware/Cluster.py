from typing import List

from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network
from vmware.models.VMware.HostSystem import HostSystem
from vmware.models.VMware.backend.Cluster import Cluster as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class Cluster(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name: str

        self.hosts: List[HostSystem] = []
        self.datastores: List[Datastore] = []
        self.networks: List[Network] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadHosts(self) -> None:
        try:
            for h in self.oHosts():
                self.hosts.append(
                    HostSystem(
                        self.assetId,
                        VmwareHelper.vmwareObjToDict(h)["moId"]
                    )
                )
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
                self.networks.append(
                    Network(
                        self.assetId,
                        VmwareHelper.vmwareObjToDict(n)["moId"]
                    )
                )
        except Exception as e:
            raise e



    def info(self, related: bool = True) -> dict:
        ho = list()
        ds = list()
        net = list()

        if related:
            self.loadHosts()
            self.loadDatastores()
            self.loadNetworks()

        # Hosts' information.
        for host in self.hosts:
            ho.append(
                Cluster.__cleanup(
                    "cluster",
                    host.info(False)
                )
            )

        # Datastores' information.
        for datastore in self.datastores:
            try:
                ds.append(
                    Cluster.__cleanup(
                        "datastore",
                        datastore.info(False)
                    )
                )
            except ValueError:
                pass

        # Networks' information.
        for network in self.networks:
            net.append(
                Cluster.__cleanup(
                    "network",
                    network.info(False)
                )
            )

        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "name": self.oCluster.name,

            "hosts": ho,
            "datastores": ds,
            "networks": net
        }



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter clusters list.
    def list(assetId, related: bool = False) -> List[dict]:
        clusters = list()

        try:
            for el in Backend.oClusters(assetId):
                data = {"assetId": assetId}
                data.update(VmwareHelper.vmwareObjToDict(el))

                if related:
                    # Add related information.
                    dc = Cluster(data["assetId"], data["moId"])

                    data.update({"hosts": dc.info()["hosts"]})
                    data.update({"datastores": dc.info()["datastores"]})
                    data.update({"networks": dc.info()["networks"]})

                clusters.append(data)

            return clusters
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        if oType == "cluster":
            if not o["datastores"]:
                del (o["datastores"])
            if not o["networks"]:
                del (o["networks"])

        if oType == "datastore":
            # List only multipleHostAccess: true.
            if o["multipleHostAccess"]:
                if not o["attachedHosts"]:
                    del (o["attachedHosts"])
            else:
                raise ValueError

        if oType == "network":
            if not o["configuredHosts"]:
                del (o["configuredHosts"])

        return o
