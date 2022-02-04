from pyVmomi import vim

from vmware.helpers.vmware.VmwareHandler import VmwareHandler


class VirtualMachine(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oVirtualMachine = self.__oVirtualMachineLoad()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # vCenter virtual machine pyVmomi objects list.
    def oVirtualMachines(assetId) -> list:
        oVirtualMachineList = list()

        try:
            vmList = VmwareHandler(assetId).getObjects(vimType=vim.VirtualMachine)
            for v in vmList:
                oVirtualMachineList.append(v)

            return oVirtualMachineList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oVirtualMachineLoad(self):
        for k, v in self.getObjects(vimType=vim.VirtualMachine, moId=self.moId).items():
            return k
