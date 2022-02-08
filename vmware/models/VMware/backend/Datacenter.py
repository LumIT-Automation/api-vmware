from pyVmomi import vim

from vmware.helpers.Exception import CustomException
from vmware.helpers.vmware.VmwareHandler import VmwareHandler


class Datacenter(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oDatacenter = self.__oDatacenterLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oClusters(self) -> list:
        try:
            return self.oDatacenter.hostFolder.childEntity
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # vCenter datacenter pyVmomi objects list.
    def oDatacenters(assetId) -> list:
        oDatacenterList = list()

        try:
            dclList = VmwareHandler(assetId).getObjects(vimType=vim.Datacenter)
            for d in dclList:
                oDatacenterList.append(d)

            return oDatacenterList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oDatacenterLoad(self):
        try:
            return self.getObjects(vimType=vim.Datacenter, moId=self.moId)[0]
        except Exception:
            raise CustomException(status=400, payload={"VMware": "cannot load resource."})
