from typing import List
from pyVmomi import vim

from vmware.models.VMware.Datastore import Datastore
from vmware.models.VMware.Network import Network
from vmware.models.VMware.backend.Cluster import Cluster as Backend

from vmware.helpers.vmware.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log



class Cluster(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name: str

        self.hosts: List[dict] = []
        self.datastores: List[Datastore] = []
        self.networks: List[Network] = []



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
                self.networks.append(
                    Network(
                        self.assetId,
                        VmwareHelper.vmwareObjToDict(n)["moId"]
                    )
                )
                #self.networks.append(VmwareHelper.vmwareObjToDict(n))
        except Exception as e:
            raise e



    def loadRelated(self):
        self.loadHosts()
        self.loadDatastores()
        self.loadNetworks()



    def info(self, related: bool = True) -> dict:
        ds = list()
        net = list()
        if related:
            self.loadRelated()

        for datastore in self.datastores:
            d = datastore.info(False)
            if not d["attachedHosts"]:
                del(d["attachedHosts"])

            # List only multipleHostAccess: true.
            if d["multipleHostAccess"]:
                ds.append(d)

        for network in self.networks:
            info = network.info(False)
            i = {
                "name": info["name"],
                "accessible": info["accessible"],
            }
            if 'vlanId' in info:
                if type(info["vlanId"]) == int:
                    i["vlanId"] = str(info["vlanId"])

                elif isinstance(info["vlanId"], list): # Trunk network here.
                    try:
                        for idRange in info["vlanId"]:
                            i["vlanId"] = str(idRange.start) + "-" + str(idRange.end)
                    except Exception:
                        pass
            net.append(i)

        return {
            "assetId": self.assetId,
            "moId": self.moId,
            "name": self.oCluster.name,
            "hosts": self.hosts,
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
