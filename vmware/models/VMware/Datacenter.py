from typing import List

from vmware.models.VMware.Cluster import Cluster
from vmware.models.VMware.HostSystem import HostSystem
from vmware.models.VMware.backend.Datacenter import Datacenter as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log


class Datacenter(Backend):
    def __init__(self, assetId: int, moId: str, name: str = "", *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name = name

        self.clusters: List[Cluster] = []
        self.standalone_hosts: List[HostSystem] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadClusters(self) -> None:
        try:
            for c in self.oClusters():
                cl = VmwareHelper.getInfo(c)

                self.clusters.append(
                    Cluster(self.assetId, cl["moId"])
                )
        except Exception as e:
            raise e



    def loadHosts(self) -> None:
        try:
            for h in self.oHosts():
                host = VmwareHelper.getInfo(h)
                self.standalone_hosts.append(
                    HostSystem(self.assetId, host["moId"])
                )
        except Exception as e:
            raise e



    def info(self, related: bool = True):
        lc = list()
        lh = list()

        try:
            if related:
                self.loadClusters()
                for cluster in self.clusters:
                    lc.append(
                        Datacenter.__cleanup("info", cluster.info(False))
                    )

                self.loadHosts()
                for host in self.standalone_hosts:
                    lh.append(
                        Datacenter.__cleanup("info", host.info(loadDatastores=False, loadNetworks=False))
                    )

            return {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": self.oDatacenter.name,
                "clusters": lc,
                "standalone_hosts": lh
            }
        except Exception as e:
            raise e



    def __contains__(self, objMoId):
        objType = VmwareHelper.getType(objMoId)

        if objType == "cluster":
            self.loadClusters()
            for cluster in self.clusters:
                if cluster.moId == objMoId:
                    return True

        if objType == "host":
            self.loadHosts()
            for host in self.standalone_hosts:
                if host.moId == objMoId:
                    return True

        return False



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, related: bool = False) -> List[dict]:
        datacenters = list()

        try:
            for o in Backend.oDatacenters(assetId):
                datacenter = Datacenter(assetId, VmwareHelper.getInfo(o)["moId"])
                datacenters.append(
                    Datacenter.__cleanup("list", datacenter.info(related))
                )

            return datacenters
        except Exception as e:
            raise e



    @staticmethod
    def listQuick(assetId: int) -> List[dict]:
        datacenters = list()

        try:
            for o in Backend.oDatacenters(assetId):
                datacenter = VmwareHelper.getInfo(o)
                datacenter["assetId"] = assetId
                datacenters.append(datacenter)

            return datacenters
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        try:
            if oType == "list":
                if not o["clusters"]:
                    del (o["clusters"])

                if not o["standalone_hosts"]:
                    del (o["standalone_hosts"])
            else:
                if not o["hosts"]:
                    del (o["hosts"])

                if not o["datastores"]:
                    del (o["datastores"])

                if not o["networks"]:
                    del (o["networks"])
        except Exception:
            pass

        return o
