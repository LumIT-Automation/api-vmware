from pyVmomi import vim

from vmware.helpers.vmware.VmwareHandler import VmwareHandler
from vmware.helpers.Log import Log


class VMFolder(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(assetId, moId, *args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oVMFolder = self.__oVMFolderLoad()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    # vCenter virtual machine pyVmomi objects list.
    def oVMFolders(assetId) -> list:
        oVMFoldersList = list()

        try:
            vmFoldersList = VmwareHandler(assetId).getObjects(vimType=vim.Folder)
            for f in vmFoldersList:
                if f.childType == [ 'Folder', 'VirtualMachine', 'VirtualApp' ]:
                    oVMFoldersList.append(f)

            return oVMFoldersList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oVMFolderLoad(self):
        return self.getObjects(vimType=vim.Folder, moId=self.moId)[0]
