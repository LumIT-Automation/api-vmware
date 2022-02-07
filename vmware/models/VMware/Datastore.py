from typing import List, TYPE_CHECKING


from vmware.models.VMware.backend.Datastore import Datastore as Backend
if TYPE_CHECKING:
    from vmware.models.VMware.HostSystem import HostSystem

from vmware.helpers.vmware.VmwareHelper import VmwareHelper


class Datastore(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name: str
        self.url: str
        self.freeSpace: int
        self.maxFileSize: int
        self.maxVirtualDiskCapacity: int
        self.type: str
        self.capacity: str
        self.multipleHostAccess: bool

        self.attachedHosts: List[HostSystem] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadAttachedHosts(self) -> None:
        from vmware.models.VMware.HostSystem import HostSystem

        try:
            for h in self.oAttachedHosts():
                c = VmwareHelper.vmwareObjToDict(h)

                self.attachedHosts.append(
                    HostSystem(self.assetId, c["moId"])
                )
        except Exception as e:
            raise e



    def info(self, related: bool = True):
        vmfsType = ""
        capacity = ""
        ssd = ""
        majorVersion = None
        local = ""
        hosts = list()

        try:
            if related:
                self.loadAttachedHosts()

            for chost in self.attachedHosts:
                hosts.append(
                    Datastore.__cleanup(
                        chost.info(loadDatastores=False, specificNetworkMoId=self.moId)
                    )
                )

            dsInfo = self.oInfoLoad()
            dsSummary = self.oSummaryLoad()

            if hasattr(dsInfo, "nas"):
                vmfsType = dsInfo.nas.type
                capacity = dsInfo.nas.capacity
            elif hasattr(dsInfo, "vmfs"):
                vmfsType = dsInfo.vmfs.type
                capacity = dsInfo.vmfs.capacity
                ssd = dsInfo.vmfs.ssd
                majorVersion = dsInfo.vmfs.majorVersion
                local = dsInfo.vmfs.local

            return {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": dsInfo.name,
                "url": dsInfo.url,
                "freeSpace": dsInfo.freeSpace,
                "maxFileSize": dsInfo.maxFileSize,
                "maxVirtualDiskCapacity": dsInfo.maxVirtualDiskCapacity,
                "multipleHostAccess": dsSummary.multipleHostAccess,
                "vmfsType": vmfsType,
                "capacity": capacity,
                "ssd": ssd,
                "majorVersion": majorVersion,
                "local": local,

                "attachedHosts": hosts
            }
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # Plain vCenter datacenters list.
    def list(assetId) -> List[dict]:
        datastores = list()

        try:
            for d in Backend.oDatastores(assetId):
                datastores.append(VmwareHelper.vmwareObjToDict(d))

            return datastores
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(o: dict):
        # Remove some related objects' information, if not loaded.
        if not o["datastores"]:
            del (o["datastores"])

        if not o["networks"]:
            del (o["networks"])

        return o
