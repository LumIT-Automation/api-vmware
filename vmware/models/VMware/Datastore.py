from typing import List, TYPE_CHECKING

from vmware.models.VMware.backend.Datastore import Datastore as Backend
if TYPE_CHECKING:
    from vmware.models.VMware.HostSystem import HostSystem

from vmware.helpers.VMware.VmwareHelper import VmwareHelper


class Datastore(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.name: str = ""
        self.url: str = ""
        self.freeSpace: int
        self.maxFileSize: int
        self.maxVirtualDiskCapacity: int
        self.vmfsType: str = ""
        self.capacity: str = ""
        self.multipleHostAccess: bool
        self.majorVersion: int = 0
        self.ssd: str = ""
        self.local: str = ""

        self.attachedHosts: List[HostSystem] = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadAttachedHosts(self) -> None:
        from vmware.models.VMware.HostSystem import HostSystem

        try:
            for h in self.oAttachedHosts():
                c = VmwareHelper.getInfo(h)

                self.attachedHosts.append(
                    HostSystem(self.assetId, c["moId"])
                )
        except Exception as e:
            raise e



    def info(self, related: bool = True):
        hosts = list()

        try:
            if related:
                self.loadAttachedHosts()
                for chost in self.attachedHosts:
                    hosts.append(
                        Datastore.__cleanup("info", chost.info(loadDatastores=False, specificNetworkMoId=self.moId))
                    )

            dsInfo = self.oInfoLoad()
            dsSummary = self.oSummaryLoad()

            if hasattr(dsInfo, "nas"):
                self.vmfsType = dsInfo.nas.type
                self.capacity = dsInfo.nas.capacity
            elif hasattr(dsInfo, "vmfs"):
                self.vmfsType = dsInfo.vmfs.type
                self.capacity = dsInfo.vmfs.capacity
                self.ssd = dsInfo.vmfs.ssd
                self.majorVersion = dsInfo.vmfs.majorVersion
                self.local = dsInfo.vmfs.local

            return {
                "assetId": self.assetId,
                "moId": self.moId,
                "name": dsInfo.name,
                "url": dsInfo.url,
                "freeSpace": dsInfo.freeSpace,
                "maxFileSize": dsInfo.maxFileSize,
                "maxVirtualDiskCapacity": dsInfo.maxVirtualDiskCapacity,
                "multipleHostAccess": dsSummary.multipleHostAccess,
                "vmfsType": self.vmfsType,
                "capacity": self.capacity,
                "ssd": self.ssd,
                "majorVersion": self.majorVersion,
                "local": self.local,

                "attachedHosts": hosts
            }
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, related: bool = False) -> List[dict]:
        datastores = list()

        try:
            for o in Backend.oDatastores(assetId):
                datastore = Datastore(assetId, VmwareHelper.getInfo(o)["moId"])
                datastores.append(
                    Datastore.__cleanup("list", datastore.info(related))
                )

            return datastores
        except Exception as e:
            raise e



    @staticmethod
    def listQuick(assetId: int) -> List[dict]:
        # No composition. Less information.
        datastores = list()

        try:
            for o in Backend.oDatastores(assetId):
                datastore = VmwareHelper.getInfo(o)
                datastore["assetId"] = assetId
                datastores.append(datastore)

            return datastores
        except Exception as e:
            raise e



    @staticmethod
    def getDatastoreMoIdByName(assetId: int, datastoreName: str):
        try:
            return Backend.getDatastoreMoIdByName(assetId, datastoreName)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __cleanup(oType: str, o: dict):
        # Remove some related objects' information, if not loaded.
        try:
            if oType == "info":
                if not o["datastores"]:
                    del (o["datastores"])

                if not o["networks"]:
                    del (o["networks"])

            if oType == "list":
                if not o["attachedHosts"]:
                    del (o["attachedHosts"])
        except Exception:
            pass

        return o
