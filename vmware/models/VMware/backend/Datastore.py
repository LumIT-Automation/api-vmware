from pyVmomi import vim

from vmware.helpers.vmware.VmwareHandler import VmwareHandler


class Datastore(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

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
    # vCenter datastore pyVmomi objects list.
    def oDatastores(assetId) -> list:
        oDatastoresList = list()

        try:
            dsList = VmwareHandler(assetId).getObjects(vimType=vim.Datastore)
            for d in dsList:
                oDatastoresList.append(d)

            return oDatastoresList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oDatastoreLoad(self):
        for k, v in self.getObjects(vimType=vim.Datastore).items():
            if k._GetMoId() == self.moId:
                return k

