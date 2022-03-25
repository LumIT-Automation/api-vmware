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

        try:
            if related:
                # Hosts' information.
                self.loadHosts()
                for host in self.hosts:
                    ho.append(
                        Cluster.__cleanup("info.cluster", host.info(loadDatastores=False, loadNetworks=False))
                    )

                # Datastores' information.
                self.loadDatastores()
                for datastore in self.datastores:
                    try:
                        ds.append(
                            Cluster.__cleanup("info.datastore", datastore.info(False))
                        )
                    except ValueError:
                        pass

                # Networks' information.
                self.loadNetworks()
                for network in self.networks:
                    net.append(
                        Cluster.__cleanup("info.network", network.info(False))
                    )

            return {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": self.oCluster.name,

                "hosts": ho,
                "datastores": ds,
                "networks": net
            }
        except Exception as e:
            raise e



    def __contains__(self, objectMoId):
        self.loadHosts()
        for host in self.hosts:
            if host.moId == objectMoId:
                return True

        self.loadDatastores()
        for datastore in self.datastores:
            if datastore.moId == objectMoId:
                return True

        self.loadNetworks()
        for network in self.networks:
            if network.moId == objectMoId:
                return True

        return False


    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, related: bool = False) -> List[dict]:
        clusters = list()

        try:
            for o in Backend.oClusters(assetId):
                cluster = Cluster(assetId, VmwareHelper.vmwareObjToDict(o)["moId"])
                clusters.append(
                    Cluster.__cleanup("list", cluster.info(related))
                )

            return clusters
        except Exception as e:
            raise e



    @staticmethod
    def listQuick(assetId: int) -> List[dict]:
        clusters = list()

        try:
            for o in Backend.oClusters(assetId):
                cluster = VmwareHelper.vmwareObjToDict(o)
                cluster["assetId"] = assetId
                clusters.append(cluster)

            return clusters
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        try:
            if oType == "info.cluster":
                if not o["datastores"]:
                    del (o["datastores"])
                if not o["networks"]:
                    del (o["networks"])

            if oType == "info.datastore":
                # List only multipleHostAccess: true.
                if o["multipleHostAccess"]:
                    if not o["attachedHosts"]:
                        del (o["attachedHosts"])
                else:
                    raise ValueError

            if oType == "info.network":
                if not o["configuredHosts"]:
                    del (o["configuredHosts"])

            if oType == "list":
                if not o["hosts"]:
                    del (o["hosts"])
                if not o["datastores"]:
                    del (o["datastores"])
                if not o["networks"]:
                    del (o["networks"])
        except Exception:
            pass

        return o
