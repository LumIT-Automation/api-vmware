from typing import List

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log

from vmware.models.VMware.backend.Datastore import Datastore as Backend


class Datastore(Backend):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId

        self.attachedHosts: List[dict] = []
        self.datastoreInfo = dict()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def loadAttachedHosts(self) -> None:
        try:
            for h in self.oAttachedHosts():
                self.attachedHosts.append(VmwareHelper.vmwareObjToDict(h))
        except Exception as e:
            raise e



    def loadInfo(self) -> None:
        info = dict()

        try:
            dsInfo = self.oInfoLoad()
            dsSummary = self.oSummaryLoad()

            info["name"] = dsInfo.name
            info["url"] = dsInfo.url
            info["freeSpace"] = dsInfo.freeSpace
            info["maxFileSize"] = dsInfo.maxFileSize
            info["maxVirtualDiskCapacity"] = dsInfo.maxVirtualDiskCapacity
            info["multipleHostAccess"] = dsSummary.multipleHostAccess

            if hasattr(dsInfo, 'nas'):
                info["type"] = dsInfo.nas.type
                info["capacity"] = dsInfo.nas.capacity
            elif hasattr(dsInfo, 'vmfs'):
                info["type"] = dsInfo.vmfs.type
                info["capacity"] = dsInfo.vmfs.capacity
                info["ssd"] = dsInfo.vmfs.ssd
                info["majorVersion"] = dsInfo.vmfs.majorVersion
                info["local"] = dsInfo.vmfs.local

            self.datastoreInfo = info
        except Exception as e:
            raise e



    def loadRelated(self):
        self.loadAttachedHosts()
        self.loadInfo()



    def info(self):
        self.loadRelated()

        return dict({
            "attachedHosts": self.attachedHosts,
            "datastoreInfo": self.datastoreInfo
        })



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
