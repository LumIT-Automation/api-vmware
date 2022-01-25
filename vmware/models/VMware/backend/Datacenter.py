from typing import List
from pyVmomi import vim, vmodl

from vmware.models.VmwareContractor import VmwareContractor

from vmware.helpers.Log import Log


class Datacenter(VmwareContractor):
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
            dclList = VmwareContractor(assetId).getContainer(vim.Datacenter)
            for d in dclList:
                oDatacenterList.append(d)

            return oDatacenterList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oDatacenterLoad(self):
        for k, v in self.getContainer(vim.Datacenter).items():
            if k._GetMoId() == self.moId:
                return k
