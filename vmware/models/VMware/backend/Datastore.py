from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler


class Datastore(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oDatastore = self.__oDatastoreLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oAttachedHosts(self) -> list:
        hosts = []

        try:
            hostMounts = self.oDatastore.host
            for h in hostMounts:
                if h.mountInfo.mounted is True and h.mountInfo.accessible is True and h.mountInfo.accessMode == "readWrite":
                    hosts.append(h.key)

            return hosts
        except Exception as e:
            raise e



    def oInfoLoad(self) -> object:
        try:
            return self.oDatastore.info
        except Exception as e:
            raise e



    def oSummaryLoad(self) -> object:
        try:
            return self.oDatastore.summary
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def oDatastores(assetId) -> list:
        try:
            return VmwareHandler().getObjects(assetId=assetId, vimType=vim.Datastore)
        except Exception as e:
            raise e



    @staticmethod
    def getDatastoreMoIdByName(assetId: int, datastoreName: str):
        try:
            dsList = Datastore.oDatastores(assetId)
            for ds in dsList:
                dsName = ds.name
                if dsName == datastoreName:
                    return ds._GetMoId()
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oDatastoreLoad(self):
        try:
            return self.getObjects(assetId=self.assetId, vimType=vim.Datastore, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=404, payload={"VMware": "Cannot load resource."})
